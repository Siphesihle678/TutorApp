#!/usr/bin/env python3
"""
Simple Railway Login Test
Tests the login functionality on Railway deployment
"""

import urllib.request
import urllib.parse
import json
import ssl

# Disable SSL verification for testing
ssl._create_default_https_context = ssl._create_unverified_context

RAILWAY_URL = "https://tutorapp-production.up.railway.app"

def test_endpoint(url, method="GET", data=None):
    """Test an endpoint and return response"""
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
        
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

def main():
    print("🚀 RAILWAY LOGIN TEST")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    health_result = test_endpoint(f"{RAILWAY_URL}/health")
    print(f"   Status: {health_result['status_code']}")
    print(f"   Response: {health_result['data'][:100]}...")
    
    # Test 2: Auth system test
    print("\n2. Testing auth system...")
    auth_test_result = test_endpoint(f"{RAILWAY_URL}/api/auth/test")
    print(f"   Status: {auth_test_result['status_code']}")
    print(f"   Response: {auth_test_result['data']}")
    
    # Test 3: Database connection test
    print("\n3. Testing database connection...")
    db_test_result = test_endpoint(f"{RAILWAY_URL}/api/quizzes/test/connection")
    print(f"   Status: {db_test_result['status_code']}")
    print(f"   Response: {db_test_result['data']}")
    
    # Test 4: Login endpoint (should return 422 for invalid data)
    print("\n4. Testing login endpoint...")
    login_data = {
        "email": "test@example.com",
        "password": "testpassword"
    }
    login_result = test_endpoint(f"{RAILWAY_URL}/api/auth/login", method="POST", data=login_data)
    print(f"   Status: {login_result['status_code']}")
    print(f"   Response: {login_result['data']}")
    
    # Summary
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print(f"{'='*50}")
    
    tests = [
        ("Health Check", health_result['status_code'] == 200),
        ("Auth System", auth_test_result['status_code'] == 200),
        ("Database", db_test_result['status_code'] == 200),
        ("Login Endpoint", login_result['status_code'] in [200, 401, 422]),  # Valid responses
    ]
    
    for test_name, passed in tests:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
    
    passed = sum(1 for _, passed in tests if passed)
    total = len(tests)
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("✅ All tests passed - Railway deployment is working!")
    else:
        print("❌ Some tests failed - check Railway logs for issues")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
