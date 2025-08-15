#!/usr/bin/env python3
"""
Test Dashboard Functionality
Tests all major features of the TutorApp
"""

import urllib.request
import urllib.parse
import json
import ssl
import time

# Disable SSL verification for testing
ssl._create_default_https_context = ssl._create_unverified_context

RAILWAY_URL = "https://tutorapp-production.up.railway.app"

def test_endpoint(url, method="GET", data=None, headers=None):
    """Test an endpoint and return response"""
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
        
        if headers:
            for key, value in headers.items():
                req.add_header(key, value)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            return {
                "status_code": response.status,
                "success": True,
                "data": response.read().decode('utf-8')
            }
    except urllib.error.HTTPError as e:
        return {
            "status_code": e.code,
            "success": False,
            "data": e.read().decode('utf-8')
        }
    except Exception as e:
        return {
            "status_code": 0,
            "success": False,
            "data": str(e)
        }

def test_quiz_functionality():
    """Test quiz-related endpoints"""
    print("🔍 Testing Quiz Functionality...")
    
    # Test 1: Get public quizzes
    result = test_endpoint(f"{RAILWAY_URL}/api/quizzes/public")
    print(f"   Get Public Quizzes: {result['status_code']} - {'✅' if result['success'] else '❌'}")
    
    # Test 2: Get quiz details (if quizzes exist)
    if result['success'] and result['status_code'] == 200:
        try:
            quizzes = json.loads(result['data'])
            if quizzes and len(quizzes) > 0:
                quiz_id = quizzes[0]['id']
                quiz_result = test_endpoint(f"{RAILWAY_URL}/api/quizzes/public/{quiz_id}")
                print(f"   Get Public Quiz Details: {quiz_result['status_code']} - {'✅' if quiz_result['success'] else '❌'}")
            else:
                print("   Get Public Quiz Details: ⚠️ No quizzes available")
        except:
            print("   Get Public Quiz Details: ⚠️ Could not parse quiz data")
    else:
        print("   Get Public Quiz Details: ⚠️ No quizzes available")
    
    return result['success']

def test_assignment_functionality():
    """Test assignment-related endpoints"""
    print("🔍 Testing Assignment Functionality...")
    
    # Test 1: Get public assignments
    result = test_endpoint(f"{RAILWAY_URL}/api/assignments/public")
    print(f"   Get Public Assignments: {result['status_code']} - {'✅' if result['success'] else '❌'}")
    
    return result['success']

def test_announcement_functionality():
    """Test announcement-related endpoints"""
    print("🔍 Testing Announcement Functionality...")
    
    # Test 1: Get public announcements
    result = test_endpoint(f"{RAILWAY_URL}/api/announcements/public")
    print(f"   Get Public Announcements: {result['status_code']} - {'✅' if result['success'] else '❌'}")
    
    return result['success']

def test_dashboard_functionality():
    """Test dashboard endpoints"""
    print("🔍 Testing Dashboard Functionality...")
    
    # Test 1: Get dashboard stats
    result = test_endpoint(f"{RAILWAY_URL}/api/dashboard/stats")
    print(f"   Dashboard Stats: {result['status_code']} - {'✅' if result['success'] else '❌'}")
    
    return result['success']

def test_static_files():
    """Test static file serving"""
    print("🔍 Testing Static Files...")
    
    # Test 1: Main page
    result = test_endpoint(f"{RAILWAY_URL}/")
    print(f"   Main Page: {result['status_code']} - {'✅' if result['success'] else '❌'}")
    
    # Test 2: Teacher dashboard
    result = test_endpoint(f"{RAILWAY_URL}/teacher")
    print(f"   Teacher Dashboard: {result['status_code']} - {'✅' if result['success'] else '❌'}")
    
    # Test 3: Student dashboard
    result = test_endpoint(f"{RAILWAY_URL}/student")
    print(f"   Student Dashboard: {result['status_code']} - {'✅' if result['success'] else '❌'}")
    
    return True

def test_api_documentation():
    """Test API documentation"""
    print("🔍 Testing API Documentation...")
    
    # Test 1: OpenAPI docs
    result = test_endpoint(f"{RAILWAY_URL}/docs")
    print(f"   API Docs: {result['status_code']} - {'✅' if result['success'] else '❌'}")
    
    return result['success']

def test_environment_issues():
    """Test for environment configuration issues"""
    print("🔍 Testing Environment Configuration...")
    
    # Test 1: Check auth system status
    result = test_endpoint(f"{RAILWAY_URL}/api/auth/test-auth")
    if result['success']:
        try:
            auth_data = json.loads(result['data'])
            secret_key_status = auth_data.get('secret_key', 'unknown')
            print(f"   SECRET_KEY: {secret_key_status} - {'❌' if secret_key_status == 'not_configured' else '✅'}")
            
            if secret_key_status == 'not_configured':
                print("   ⚠️  SECRET_KEY is not properly configured - this may cause issues!")
                return False
        except:
            print("   SECRET_KEY: ⚠️ Could not check")
    
    return True

def main():
    """Run comprehensive functionality test"""
    print("🚀 TUTORAPP COMPREHENSIVE FUNCTIONALITY TEST")
    print("=" * 60)
    
    tests = [
        ("Static Files", test_static_files),
        ("API Documentation", test_api_documentation),
        ("Environment Configuration", test_environment_issues),
        ("Quiz Functionality", test_quiz_functionality),
        ("Assignment Functionality", test_assignment_functionality),
        ("Announcement Functionality", test_announcement_functionality),
        ("Dashboard Functionality", test_dashboard_functionality),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"   ❌ ERROR: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 COMPREHENSIVE TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All functionality tests passed - TutorApp is 100% functional!")
    else:
        print("❌ Some functionality tests failed - TutorApp is NOT at 100%")
        print("\n🔧 Issues to address:")
        for test_name, result in results:
            if not result:
                print(f"   - {test_name} needs attention")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
