#!/usr/bin/env python3
"""
Simple Login Test
Tests basic login functionality
"""

import urllib.request
import urllib.parse
import json
import ssl

# Disable SSL verification for testing
ssl._create_default_https_context = ssl._create_unverified_context

RAILWAY_URL = "https://tutorapp-production.up.railway.app"

def test_simple_login():
    """Test a simple login attempt"""
    print("🚀 SIMPLE LOGIN TEST")
    print("=" * 40)
    
    # Test data
    login_data = {
        "email": "test@example.com",
        "password": "testpassword123"
    }
    
    try:
        # Create request
        data = json.dumps(login_data).encode('utf-8')
        req = urllib.request.Request(f"{RAILWAY_URL}/api/auth/login", data=data, method="POST")
        req.add_header('Content-Type', 'application/json')
        
        # Make request
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(f"✅ Login successful!")
            print(f"   Status: {response.status}")
            print(f"   Response: {result}")
            return True
            
    except urllib.error.HTTPError as e:
        result = e.read().decode('utf-8')
        print(f"📋 Login response (expected for test user):")
        print(f"   Status: {e.code}")
        print(f"   Response: {result}")
        
        # 401 is expected for non-existent user
        if e.code == 401:
            print("✅ Login endpoint is working correctly!")
            return True
        else:
            print("❌ Unexpected error")
            return False
            
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    success = test_simple_login()
    exit(0 if success else 1)
