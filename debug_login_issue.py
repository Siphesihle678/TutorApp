#!/usr/bin/env python3
"""
Debug Login Issue Script
Identifies the specific cause of the login failure
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing imports...")
    
    try:
        from app.core.database import get_db, engine
        print("✅ Database imports successful")
    except Exception as e:
        print(f"❌ Database import failed: {e}")
        return False
    
    try:
        from app.core.security import verify_password, get_password_hash, create_access_token
        print("✅ Security imports successful")
    except Exception as e:
        print(f"❌ Security import failed: {e}")
        return False
    
    try:
        from app.core.config import settings
        print("✅ Config imports successful")
    except Exception as e:
        print(f"❌ Config import failed: {e}")
        return False
    
    try:
        from app.models.user import User
        print("✅ User model import successful")
    except Exception as e:
        print(f"❌ User model import failed: {e}")
        return False
    
    try:
        from app.routes.auth import router
        print("✅ Auth router import successful")
    except Exception as e:
        print(f"❌ Auth router import failed: {e}")
        return False
    
    return True

def test_database_connection():
    """Test database connection"""
    print("\n🔍 Testing database connection...")
    
    try:
        from app.core.database import engine
        from app.core.config import settings
        
        print(f"Database URL: {settings.DATABASE_URL[:50]}...")
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print("✅ Database connection successful")
            return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def test_user_creation():
    """Test user creation and login process"""
    print("\n🔍 Testing user creation and login...")
    
    try:
        from app.core.database import get_db
        from app.models.user import User
        from app.core.security import get_password_hash, verify_password, create_access_token
        
        # Get database session
        db = next(get_db())
        
        # Test password hashing
        test_password = "testpassword123"
        hashed_password = get_password_hash(test_password)
        print("✅ Password hashing successful")
        
        # Test password verification
        is_valid = verify_password(test_password, hashed_password)
        print(f"✅ Password verification: {is_valid}")
        
        # Test token creation
        token_data = {"sub": "test@example.com"}
        token = create_access_token(token_data)
        print("✅ Token creation successful")
        
        db.close()
        return True
    except Exception as e:
        print(f"❌ User creation/login test failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_environment_variables():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    try:
        from app.core.config import settings
        
        print(f"SECRET_KEY: {'Set' if settings.SECRET_KEY else 'Not set'}")
        print(f"DATABASE_URL: {'Set' if settings.DATABASE_URL else 'Not set'}")
        print(f"ALGORITHM: {settings.ALGORITHM}")
        print(f"ACCESS_TOKEN_EXPIRE_MINUTES: {settings.ACCESS_TOKEN_EXPIRE_MINUTES}")
        
        if not settings.SECRET_KEY or settings.SECRET_KEY == "your-secret-key-change-in-production":
            print("⚠️  SECRET_KEY is not properly configured")
            return False
        
        if not settings.DATABASE_URL:
            print("⚠️  DATABASE_URL is not set")
            return False
        
        print("✅ Environment variables look good")
        return True
    except Exception as e:
        print(f"❌ Environment variable test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 TUTORAPP LOGIN ISSUE DEBUG")
    print("=" * 50)
    
    tests = [
        ("Imports", test_imports),
        ("Environment Variables", test_environment_variables),
        ("Database Connection", test_database_connection),
        ("User Creation/Login", test_user_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 DEBUG SUMMARY")
    print(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed - login should work")
    else:
        print("❌ Issues detected - check the failed tests above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
