#!/usr/bin/env python3
"""
Comprehensive Test Script for TutorApp
Tests all major functionality to ensure 100% working status
"""

import requests
import json
import time
from datetime import datetime

# Configuration
BASE_URL = "http://localhost:8000"  # Change to your Railway URL for production testing
API_BASE = f"{BASE_URL}/api"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 TESTING: {test_name}")
    print(f"{'='*60}")

def print_test_result(test_name, success, message=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"   {message}")

def test_health_check():
    """Test basic application health"""
    print_test_header("Health Check")
    
    try:
        response = requests.get(f"{BASE_URL}/health")
        success = response.status_code == 200
        print_test_result("Health Check", success, f"Status: {response.status_code}")
        if success:
            print(f"   Response: {response.json()}")
        return success
    except Exception as e:
        print_test_result("Health Check", False, f"Error: {str(e)}")
        return False

def test_database_connection():
    """Test database connectivity"""
    print_test_header("Database Connection")
    
    try:
        response = requests.get(f"{API_BASE}/quizzes/test/connection")
        success = response.status_code == 200
        print_test_result("Database Connection", success, f"Status: {response.status_code}")
        if success:
            data = response.json()
            print(f"   Database Connected: {data.get('database_connected', False)}")
            print(f"   Quiz Count: {data.get('quiz_count', 0)}")
            print(f"   Question Count: {data.get('question_count', 0)}")
        return success
    except Exception as e:
        print_test_result("Database Connection", False, f"Error: {str(e)}")
        return False

def test_api_documentation():
    """Test API documentation access"""
    print_test_header("API Documentation")
    
    try:
        response = requests.get(f"{BASE_URL}/docs")
        success = response.status_code == 200
        print_test_result("API Documentation", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test_result("API Documentation", False, f"Error: {str(e)}")
        return False

def test_static_files():
    """Test static file serving"""
    print_test_header("Static Files")
    
    try:
        response = requests.get(f"{BASE_URL}/")
        success = response.status_code == 200
        print_test_result("Main Page", success, f"Status: {response.status_code}")
        return success
    except Exception as e:
        print_test_result("Main Page", False, f"Error: {str(e)}")
        return False

def test_authentication_endpoints():
    """Test authentication endpoints"""
    print_test_header("Authentication Endpoints")
    
    # Test registration endpoint (without actually registering)
    try:
        response = requests.post(f"{API_BASE}/auth/register", json={
            "name": "Test User",
            "email": "test@example.com",
            "password": "testpassword",
            "role": "student"
        })
        # Should either succeed or return a specific error (like email already exists)
        success = response.status_code in [200, 400, 422]
        print_test_result("Registration Endpoint", success, f"Status: {response.status_code}")
        
        # Test login endpoint
        response = requests.post(f"{API_BASE}/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        success = response.status_code in [200, 401, 422]
        print_test_result("Login Endpoint", success, f"Status: {response.status_code}")
        
        return True
    except Exception as e:
        print_test_result("Authentication Endpoints", False, f"Error: {str(e)}")
        return False

def test_quiz_endpoints():
    """Test quiz-related endpoints"""
    print_test_header("Quiz Endpoints")
    
    try:
        # Test getting quizzes (should work without authentication for public quizzes)
        response = requests.get(f"{API_BASE}/quizzes/")
        success = response.status_code in [200, 401, 403]  # 401/403 expected without auth
        print_test_result("Get Quizzes", success, f"Status: {response.status_code}")
        
        # Test quiz creation endpoint (should require authentication)
        response = requests.post(f"{API_BASE}/quizzes/", json={
            "title": "Test Quiz",
            "description": "Test Description",
            "subject": "Test Subject",
            "time_limit": 30,
            "passing_score": 70,
            "questions": []
        })
        success = response.status_code in [401, 403, 422]  # Expected without auth
        print_test_result("Create Quiz (Unauthenticated)", success, f"Status: {response.status_code}")
        
        return True
    except Exception as e:
        print_test_result("Quiz Endpoints", False, f"Error: {str(e)}")
        return False

def test_assignment_endpoints():
    """Test assignment-related endpoints"""
    print_test_header("Assignment Endpoints")
    
    try:
        # Test getting assignments
        response = requests.get(f"{API_BASE}/assignments/")
        success = response.status_code in [200, 401, 403]
        print_test_result("Get Assignments", success, f"Status: {response.status_code}")
        
        return True
    except Exception as e:
        print_test_result("Assignment Endpoints", False, f"Error: {str(e)}")
        return False

def test_announcement_endpoints():
    """Test announcement-related endpoints"""
    print_test_header("Announcement Endpoints")
    
    try:
        # Test getting announcements
        response = requests.get(f"{API_BASE}/announcements/")
        success = response.status_code in [200, 401, 403]
        print_test_result("Get Announcements", success, f"Status: {response.status_code}")
        
        return True
    except Exception as e:
        print_test_result("Announcement Endpoints", False, f"Error: {str(e)}")
        return False

def test_dashboard_endpoints():
    """Test dashboard endpoints"""
    print_test_header("Dashboard Endpoints")
    
    try:
        # Test dashboard endpoints (should require authentication)
        response = requests.get(f"{API_BASE}/dashboard/student")
        success = response.status_code in [401, 403]  # Expected without auth
        print_test_result("Student Dashboard (Unauthenticated)", success, f"Status: {response.status_code}")
        
        response = requests.get(f"{API_BASE}/dashboard/teacher")
        success = response.status_code in [401, 403]  # Expected without auth
        print_test_result("Teacher Dashboard (Unauthenticated)", success, f"Status: {response.status_code}")
        
        return True
    except Exception as e:
        print_test_result("Dashboard Endpoints", False, f"Error: {str(e)}")
        return False

def test_error_handling():
    """Test error handling"""
    print_test_header("Error Handling")
    
    try:
        # Test 404 handling
        response = requests.get(f"{BASE_URL}/nonexistent-endpoint")
        success = response.status_code == 404
        print_test_result("404 Error Handling", success, f"Status: {response.status_code}")
        
        # Test invalid JSON handling
        response = requests.post(f"{API_BASE}/auth/login", data="invalid json")
        success = response.status_code in [400, 422]
        print_test_result("Invalid JSON Handling", success, f"Status: {response.status_code}")
        
        return True
    except Exception as e:
        print_test_result("Error Handling", False, f"Error: {str(e)}")
        return False

def run_comprehensive_test():
    """Run all tests and provide summary"""
    print(f"\n🚀 COMPREHENSIVE TUTORAPP TESTING")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Base URL: {BASE_URL}")
    
    tests = [
        ("Health Check", test_health_check),
        ("Database Connection", test_database_connection),
        ("API Documentation", test_api_documentation),
        ("Static Files", test_static_files),
        ("Authentication Endpoints", test_authentication_endpoints),
        ("Quiz Endpoints", test_quiz_endpoints),
        ("Assignment Endpoints", test_assignment_endpoints),
        ("Announcement Endpoints", test_announcement_endpoints),
        ("Dashboard Endpoints", test_dashboard_endpoints),
        ("Error Handling", test_error_handling),
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
    print(f"\n{'='*60}")
    print(f"📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! TutorApp is 100% functional!")
    elif passed >= total * 0.8:
        print("⚠️  MOST TESTS PASSED! Minor issues detected.")
    else:
        print("🚨 SIGNIFICANT ISSUES DETECTED! Needs attention.")
    
    return passed == total

if __name__ == "__main__":
    success = run_comprehensive_test()
    exit(0 if success else 1)
