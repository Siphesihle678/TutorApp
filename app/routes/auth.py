from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..core.database import get_db
from ..core.security import get_password_hash, verify_password, create_access_token
from ..core.auth import get_current_user
from ..core.utils import generate_unique_tutor_code, find_tutor_by_code
from ..models.user import User
from ..schemas.user import UserCreate, UserRead, UserLogin, Token, UserUpdate

router = APIRouter()

@router.post("/register", response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if user already exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Handle tutor registration
    if user.role == "teacher":
        # Generate unique tutor code for new teachers
        tutor_code = generate_unique_tutor_code(db)
        tutor_id = None
    else:
        # Handle student registration with tutor code
        tutor_id = None
        if user.tutor_code:
            # Find tutor by code
            tutor = find_tutor_by_code(db, user.tutor_code)
            if not tutor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tutor code. Please check with your tutor."
                )
            tutor_id = tutor.id
        elif user.tutor_id:
            # Fallback to tutor_id if provided
            tutor = db.query(User).filter(
                User.id == user.tutor_id,
                User.role == "teacher",
                User.is_active == True
            ).first()
            if not tutor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tutor ID or tutor not found"
                )
            tutor_id = user.tutor_id
    
    # Create new user
    hashed_password = get_password_hash(user.password)
    db_user = User(
        name=user.name,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        tutor_id=tutor_id,
        tutor_code=tutor_code if user.role == "teacher" else None
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    return db_user

@router.post("/login", response_model=Token)
def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user and return access token"""
    try:
        print(f"=== LOGIN ATTEMPT ===")
        print(f"Email: {user_credentials.email}")
        
        # Step 1: Find user
        print("Step 1: Finding user...")
        user = db.query(User).filter(User.email == user_credentials.email).first()
        if not user:
            print("ERROR: User not found")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Step 2: Verify password
        print("Step 2: Verifying password...")
        if not verify_password(user_credentials.password, user.hashed_password):
            print("ERROR: Invalid password")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Step 3: Check if user is active
        print("Step 3: Checking user status...")
        if not user.is_active:
            print("ERROR: User account is deactivated")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Account is deactivated"
            )
        
        # Step 4: Create access token
        print("Step 4: Creating access token...")
        access_token = create_access_token(data={"sub": user.email})
        
        print("=== LOGIN SUCCESS ===")
        return {"access_token": access_token, "token_type": "bearer"}
        
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        print(f"=== LOGIN ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        
        # Return a proper error response
        raise HTTPException(
            status_code=500,
            detail="An internal server error occurred during login. Please try again."
        )

@router.get("/validate-tutor-code/{tutor_code}")
def validate_tutor_code(tutor_code: str, db: Session = Depends(get_db)):
    """Validate a tutor code and return tutor information"""
    tutor = find_tutor_by_code(db, tutor_code)
    
    if not tutor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid tutor code. Please check with your tutor."
        )
    
    return {
        "valid": True,
        "tutor_name": tutor.name,
        "tutor_email": tutor.email,
        "student_count": len(tutor.students) if tutor.students else 0
    }

@router.get("/me/tutor-code")
def get_my_tutor_code(current_user: User = Depends(get_current_user)):
    """Get current user's tutor code (for teachers only)"""
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can access tutor codes"
        )
    
    if not current_user.tutor_code:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No tutor code found for this account"
        )
    
    return {
        "tutor_code": current_user.tutor_code,
        "name": current_user.name,
        "email": current_user.email
    }

@router.get("/me", response_model=UserRead)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current user information"""
    return current_user

@router.get("/test-auth")
def test_auth_system():
    """Test authentication system health"""
    try:
        from app.core.config import settings
        from app.core.database import engine
        
        # Test database connection
        with engine.connect() as conn:
            from sqlalchemy import text
            conn.execute(text("SELECT 1"))
        
        return {
            "status": "healthy",
            "database": "connected",
            "secret_key": "configured" if settings.SECRET_KEY and settings.SECRET_KEY != "your-secret-key-change-in-production" else "not_configured",
            "algorithm": settings.ALGORITHM,
            "token_expiry": f"{settings.ACCESS_TOKEN_EXPIRE_MINUTES} minutes"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "error_type": type(e).__name__
        }

@router.put("/me", response_model=UserRead)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user information"""
    if user_update.name is not None:
        current_user.name = user_update.name
    if user_update.email is not None:
        # Check if email is already taken
        existing_user = db.query(User).filter(
            User.email == user_update.email,
            User.id != current_user.id
        ).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already taken"
            )
        current_user.email = user_update.email
    if user_update.is_active is not None:
        current_user.is_active = user_update.is_active
    if user_update.tutor_id is not None:
        # Validate tutor assignment
        if user_update.tutor_id != current_user.tutor_id:  # Only validate if changing
            tutor = db.query(User).filter(
                User.id == user_update.tutor_id,
                User.role == "teacher",
                User.is_active == True
            ).first()
            if not tutor:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid tutor ID or tutor not found"
                )
        current_user.tutor_id = user_update.tutor_id
    
    db.commit()
    db.refresh(current_user)
    return current_user
