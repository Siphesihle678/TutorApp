#!/usr/bin/env python3
"""
Simple test script to debug login issues
"""

import requests
import json

# Test the login endpoint
def test_login():
    url = "https://tutorapp-production.up.railway.app/api/auth/login"
    
    # Test data - use a known teacher account
    test_data = {
        "email": "teacher@example.com",  # Replace with actual email
        "password": "password123"        # Replace with actual password
    }
    
    try:
        print("🔍 Testing login endpoint...")
        print(f"URL: {url}")
        print(f"Data: {json.dumps(test_data, indent=2)}")
        
        response = requests.post(url, json=test_data, timeout=30)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")

def test_health():
    """Test if the server is responding at all"""
    url = "https://tutorapp-production.up.railway.app/"
    
    try:
        print("🔍 Testing server health...")
        response = requests.get(url, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text[:200]}...")
    except Exception as e:
        print(f"❌ Health check failed: {e}")

if __name__ == "__main__":
    print("🚀 Starting TutorApp Login Debug Test")
    print("=" * 50)
    
    test_health()
    print("\n" + "=" * 50)
    test_login()
