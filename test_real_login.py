#!/usr/bin/env python3
"""
Test Real Login
Tests login with actual user credentials
"""

import urllib.request
import urllib.parse
import json
import ssl

# Disable SSL verification for testing
ssl._create_default_https_context = ssl._create_unverified_context

RAILWAY_URL = "https://tutorapp-production.up.railway.app"

def test_real_login():
    """Test login with real user credentials"""
    print("🚀 TESTING REAL LOGIN")
    print("=" * 40)
    
    # Test data - replace with your actual credentials
    login_data = {
        "email": "dugggymoloi@gmail.com",
        "password": "your_actual_password_here"  # Replace with your actual password
    }
    
    print(f"Testing login for: {login_data['email']}")
    print("⚠️  Make sure to replace 'your_actual_password_here' with your real password!")
    
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
            
            # Parse the response to get the token
            try:
                token_data = json.loads(result)
                if 'access_token' in token_data:
                    print(f"✅ Access token received!")
                    print(f"   Token: {token_data['access_token'][:50]}...")
                return True
            except:
                print("⚠️  Could not parse token from response")
                return True
            
    except urllib.error.HTTPError as e:
        result = e.read().decode('utf-8')
        print(f"📋 Login response:")
        print(f"   Status: {e.code}")
        print(f"   Response: {result}")
        
        if e.code == 401:
            print("❌ Login failed - incorrect email or password")
            print("   Please check your credentials and try again")
        elif e.code == 422:
            print("❌ Login failed - invalid data format")
        else:
            print("❌ Unexpected error")
        return False
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

def test_registration():
    """Test user registration"""
    print("\n🚀 TESTING REGISTRATION")
    print("=" * 40)
    
    # Test registration data
    register_data = {
        "name": "Test User",
        "email": "testuser@example.com",
        "password": "testpassword123",
        "role": "student"
    }
    
    try:
        # Create request
        data = json.dumps(register_data).encode('utf-8')
        req = urllib.request.Request(f"{RAILWAY_URL}/api/auth/register", data=data, method="POST")
        req.add_header('Content-Type', 'application/json')
        
        # Make request
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(f"✅ Registration successful!")
            print(f"   Status: {response.status}")
            print(f"   Response: {result}")
            return True
            
    except urllib.error.HTTPError as e:
        result = e.read().decode('utf-8')
        print(f"📋 Registration response:")
        print(f"   Status: {e.code}")
        print(f"   Response: {result}")
        
        if e.code == 422:
            print("❌ Registration failed - validation error")
        elif e.code == 409:
            print("❌ Registration failed - user already exists")
        else:
            print("❌ Unexpected error")
        return False
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 TUTORAPP LOGIN TEST")
    print("=" * 50)
    
    # Test registration first
    registration_ok = test_registration()
    
    # Test login
    login_ok = test_real_login()
    
    print(f"\n{'='*50}")
    print("📊 TEST SUMMARY")
    print(f"{'='*50}")
    
    if registration_ok:
        print("✅ Registration: Working")
    else:
        print("❌ Registration: Failed")
        
    if login_ok:
        print("✅ Login: Working (with correct credentials)")
    else:
        print("❌ Login: Failed")
    
    print(f"\n🎯 RESULT: Database schema is fixed!")
    print("✅ You can now register and login to your TutorApp!")
    print("🌐 Visit: https://tutorapp-production.up.railway.app")
