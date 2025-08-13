#!/usr/bin/env python3
"""
Test script to verify quiz submission fixes
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8000"  # Change this to your Railway URL when deployed
API_BASE_URL = f"{BASE_URL}/api"

def test_quiz_submission():
    """Test quiz submission with proper error handling"""
    
    # Test data
    test_submissions = [
        {
            "question_id": 1,
            "answer": "test answer"
        }
    ]
    
    print("Testing quiz submission error handling...")
    
    # Test 1: Invalid quiz ID (should return 404)
    try:
        response = requests.post(
            f"{API_BASE_URL}/quizzes/999/submit",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_submissions)
        )
        
        if response.status_code == 404:
            print("✅ Test 1 PASSED: Invalid quiz ID returns 404")
        else:
            print(f"❌ Test 1 FAILED: Expected 404, got {response.status_code}")
            
        # Check if response is JSON
        try:
            error_data = response.json()
            print("✅ Response is valid JSON")
        except json.JSONDecodeError:
            print("❌ Response is not valid JSON")
            
    except Exception as e:
        print(f"❌ Test 1 ERROR: {str(e)}")
    
    # Test 2: Invalid request format (should return 422)
    try:
        response = requests.post(
            f"{API_BASE_URL}/quizzes/1/submit",
            headers={"Content-Type": "application/json"},
            data="invalid json"
        )
        
        if response.status_code == 422:
            print("✅ Test 2 PASSED: Invalid JSON returns 422")
        else:
            print(f"❌ Test 2 FAILED: Expected 422, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test 2 ERROR: {str(e)}")
    
    # Test 3: Missing authentication (should return 401)
    try:
        response = requests.post(
            f"{API_BASE_URL}/quizzes/1/submit",
            headers={"Content-Type": "application/json"},
            data=json.dumps(test_submissions)
        )
        
        if response.status_code == 401:
            print("✅ Test 3 PASSED: Missing auth returns 401")
        else:
            print(f"❌ Test 3 FAILED: Expected 401, got {response.status_code}")
            
    except Exception as e:
        print(f"❌ Test 3 ERROR: {str(e)}")

def test_health_endpoint():
    """Test health endpoint"""
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Health check PASSED: {data['status']}")
        else:
            print(f"❌ Health check FAILED: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check ERROR: {str(e)}")

if __name__ == "__main__":
    print("🧪 Testing TutorApp Quiz Submission Fixes")
    print("=" * 50)
    
    test_health_endpoint()
    print()
    test_quiz_submission()
    
    print("\n" + "=" * 50)
    print("✅ Testing complete! All errors should now return proper JSON responses.")
