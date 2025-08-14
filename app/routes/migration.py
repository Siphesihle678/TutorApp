from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from ..core.database import get_db, engine
from ..core.auth import get_current_user
from ..models.user import User

router = APIRouter()

@router.post("/migrate-subject-grade")
def migrate_subject_grade_system(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Run migration to add subject/grade tables (admin only)"""
    # Only allow teachers to run migration for now
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can run migrations"
        )
    
    try:
        # Check if subjects table already exists
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'subjects'
        """))
        
        if not result.fetchone():
            # Create subjects table
            db.execute(text("""
                CREATE TABLE subjects (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    description TEXT,
                    tutor_id INTEGER NOT NULL REFERENCES users(id),
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ
                )
            """))
            
            # Create index on tutor_id
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_subjects_tutor_id 
                ON subjects (tutor_id)
            """))
            
            print("✅ Successfully created subjects table")
        else:
            print("✅ subjects table already exists")
        
        # Check if grades table already exists
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'grades'
        """))
        
        if not result.fetchone():
            # Create grades table
            db.execute(text("""
                CREATE TABLE grades (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
                    is_active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMPTZ DEFAULT NOW(),
                    updated_at TIMESTAMPTZ
                )
            """))
            
            # Create index on subject_id
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_grades_subject_id 
                ON grades (subject_id)
            """))
            
            print("✅ Successfully created grades table")
        else:
            print("✅ grades table already exists")
        
        # Check if student_grades table already exists
        result = db.execute(text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_name = 'student_grades'
        """))
        
        if not result.fetchone():
            # Create student_grades table
            db.execute(text("""
                CREATE TABLE student_grades (
                    id SERIAL PRIMARY KEY,
                    student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                    grade_id INTEGER NOT NULL REFERENCES grades(id) ON DELETE CASCADE,
                    enrolled_at TIMESTAMPTZ DEFAULT NOW(),
                    is_active BOOLEAN DEFAULT TRUE,
                    UNIQUE(student_id, grade_id)
                )
            """))
            
            # Create indexes
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_student_grades_student_id 
                ON student_grades (student_id)
            """))
            
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_student_grades_grade_id 
                ON student_grades (grade_id)
            """))
            
            print("✅ Successfully created student_grades table")
        else:
            print("✅ student_grades table already exists")
        
        # Add subject_id and grade_id columns to quizzes table if they don't exist
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'quizzes' AND column_name = 'subject_id'
        """))
        
        if not result.fetchone():
            db.execute(text("""
                ALTER TABLE quizzes 
                ADD COLUMN subject_id INTEGER REFERENCES subjects(id)
            """))
            print("✅ Added subject_id column to quizzes table")
        else:
            print("✅ subject_id column already exists in quizzes table")
        
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'quizzes' AND column_name = 'grade_id'
        """))
        
        if not result.fetchone():
            db.execute(text("""
                ALTER TABLE quizzes 
                ADD COLUMN grade_id INTEGER REFERENCES grades(id)
            """))
            print("✅ Added grade_id column to quizzes table")
        else:
            print("✅ grade_id column already exists in quizzes table")
        
        # Add subject_id and grade_id columns to assignments table if they don't exist
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'assignments' AND column_name = 'subject_id'
        """))
        
        if not result.fetchone():
            db.execute(text("""
                ALTER TABLE assignments 
                ADD COLUMN subject_id INTEGER REFERENCES subjects(id)
            """))
            print("✅ Added subject_id column to assignments table")
        else:
            print("✅ subject_id column already exists in assignments table")
        
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'assignments' AND column_name = 'grade_id'
        """))
        
        if not result.fetchone():
            db.execute(text("""
                ALTER TABLE assignments 
                ADD COLUMN grade_id INTEGER REFERENCES grades(id)
            """))
            print("✅ Added grade_id column to assignments table")
        else:
            print("✅ grade_id column already exists in assignments table")
        
        db.commit()
        
        return {
            "message": "Migration completed successfully",
            "status": "success",
            "details": "Subject/grade tables and columns have been created"
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error during migration: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Migration failed: {str(e)}"
        )

@router.post("/create-default-subjects")
def create_default_subjects(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create default subjects for the current teacher"""
    if current_user.role != "teacher":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only teachers can create subjects"
        )
    
    try:
        default_subjects = [
            {"name": "CAT", "description": "Computer Applications Technology"},
            {"name": "Mathematics", "description": "Mathematics"},
            {"name": "English", "description": "English Language"},
            {"name": "Physics", "description": "Physics"},
            {"name": "Accounting", "description": "Accounting"}
        ]
        
        created_subjects = []
        
        for subject_data in default_subjects:
            # Check if subject already exists for this teacher
            existing = db.execute(text("""
                SELECT id FROM subjects 
                WHERE tutor_id = :tutor_id AND name = :name
            """), {"tutor_id": current_user.id, "name": subject_data["name"]}).fetchone()
            
            if not existing:
                # Create subject
                result = db.execute(text("""
                    INSERT INTO subjects (name, description, tutor_id) 
                    VALUES (:name, :description, :tutor_id) 
                    RETURNING id
                """), {
                    "name": subject_data["name"],
                    "description": subject_data["description"],
                    "tutor_id": current_user.id
                })
                
                subject_id = result.fetchone()[0]
                
                # Create default grades for this subject
                default_grades = ["Grade 10", "Grade 11", "Grade 12"]
                for grade_name in default_grades:
                    db.execute(text("""
                        INSERT INTO grades (name, subject_id) 
                        VALUES (:name, :subject_id)
                    """), {"name": grade_name, "subject_id": subject_id})
                
                created_subjects.append(subject_data["name"])
                print(f"✅ Created subject '{subject_data['name']}' with grades")
            else:
                print(f"⚠️  Subject '{subject_data['name']}' already exists")
        
        db.commit()
        
        return {
            "message": "Default subjects created successfully",
            "created_subjects": created_subjects,
            "teacher": current_user.name
        }
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error creating default subjects: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create default subjects: {str(e)}"
        )

@router.post("/fix-schema")
def fix_database_schema(db: Session = Depends(get_db)):
    """Fix database schema by adding missing columns"""
    try:
        print("🔧 FIXING DATABASE SCHEMA")
        
        # Check if tutor_id column exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'tutor_id'
        """))
        
        if result.fetchone():
            print("✅ tutor_id column already exists")
        else:
            print("❌ tutor_id column missing - adding it...")
            
            # Add the tutor_id column
            db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN tutor_id INTEGER
            """))
            
            # Create index on tutor_id
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_tutor_id 
                ON users(tutor_id)
            """))
            
            print("✅ tutor_id column added successfully")
        
        # Check if tutor_code column exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'tutor_code'
        """))
        
        if result.fetchone():
            print("✅ tutor_code column already exists")
        else:
            print("❌ tutor_code column missing - adding it...")
            
            # Add the tutor_code column
            db.execute(text("""
                ALTER TABLE users 
                ADD COLUMN tutor_code VARCHAR
            """))
            
            # Create index on tutor_code
            db.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_users_tutor_code 
                ON users(tutor_code)
            """))
            
            print("✅ tutor_code column added successfully")
        
        # Commit the changes
        db.commit()
        print("✅ Database schema updated successfully")
        
        return {
            "status": "success",
            "message": "Database schema updated successfully",
            "changes": [
                "Added tutor_id column if missing",
                "Added tutor_code column if missing",
                "Created indexes for better performance"
            ]
        }
        
    except Exception as e:
        print(f"❌ Database schema fix failed: {e}")
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Database schema fix failed: {str(e)}"
        )

@router.get("/schema-status")
def check_schema_status(db: Session = Depends(get_db)):
    """Check the current database schema status"""
    try:
        # Check if tutor_id column exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'tutor_id'
        """))
        tutor_id_exists = result.fetchone() is not None
        
        # Check if tutor_code column exists
        result = db.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'tutor_code'
        """))
        tutor_code_exists = result.fetchone() is not None
        
        return {
            "status": "success",
            "schema_status": {
                "tutor_id_column": "exists" if tutor_id_exists else "missing",
                "tutor_code_column": "exists" if tutor_code_exists else "missing",
                "needs_fix": not (tutor_id_exists and tutor_code_exists)
            }
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Schema status check failed: {str(e)}"
        )

