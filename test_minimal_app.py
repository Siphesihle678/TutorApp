#!/usr/bin/env python3
"""
Minimal App Test
Tests a minimal version of the app without problematic imports
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def test_minimal_imports():
    """Test minimal imports without Subject model"""
    print("🔍 Testing minimal imports...")
    
    try:
        # Test core imports
        from app.core.config import settings
        print("✅ Config imported")
        
        from app.core.database import engine, Base
        print("✅ Database imported")
        
        from app.models.user import User
        print("✅ User model imported")
        
        from app.models.quiz import Quiz, Question
        print("✅ Quiz models imported")
        
        from app.models.assignment import Assignment
        print("✅ Assignment model imported")
        
        from app.models.announcement import Announcement
        print("✅ Announcement model imported")
        
        from app.models.performance import PerformanceRecord
        print("✅ Performance model imported")
        
        return True
    except Exception as e:
        print(f"❌ Import failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_database_creation():
    """Test database table creation"""
    print("\n🔍 Testing database table creation...")
    
    try:
        from app.core.database import engine, Base
        from app.models.user import User
        from app.models.quiz import Quiz, Question, QuizAttempt, QuizSubmission
        from app.models.assignment import Assignment, AssignmentSubmission
        from app.models.announcement import Announcement
        from app.models.performance import PerformanceRecord
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_auth_functionality():
    """Test authentication functionality"""
    print("\n🔍 Testing authentication functionality...")
    
    try:
        from app.core.security import get_password_hash, verify_password, create_access_token
        from app.core.config import settings
        
        # Test password hashing
        password = "testpassword123"
        hashed = get_password_hash(password)
        print("✅ Password hashing works")
        
        # Test password verification
        is_valid = verify_password(password, hashed)
        print(f"✅ Password verification: {is_valid}")
        
        # Test token creation
        token = create_access_token({"sub": "test@example.com"})
        print("✅ Token creation works")
        
        return True
    except Exception as e:
        print(f"❌ Auth functionality failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def main():
    """Run all tests"""
    print("🚀 MINIMAL APP TEST")
    print("=" * 50)
    
    tests = [
        ("Minimal Imports", test_minimal_imports),
        ("Database Creation", test_database_creation),
        ("Auth Functionality", test_auth_functionality),
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
    print("📊 TEST SUMMARY")
    print(f"{'='*50}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed - core functionality works")
    else:
        print("❌ Issues detected - check the failed tests above")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
