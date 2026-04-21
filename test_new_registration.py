#!/usr/bin/env python3
"""
Test New Registration
Tests registration with a new email address
"""

import urllib.request
import urllib.parse
import json
import ssl
import time

# Disable SSL verification for testing
ssl._create_default_https_context = ssl._create_unverified_context

RAILWAY_URL = "https://tutorapp-production.up.railway.app"

def test_new_registration():
    """Test registration with a new email"""
    print("🚀 TESTING NEW REGISTRATION")
    print("=" * 40)
    
    # Generate unique email using timestamp
    timestamp = int(time.time())
    test_email = f"testuser{timestamp}@example.com"
    
    # Test registration data
    register_data = {
        "name": "Test User",
        "email": test_email,
        "password": "testpassword123",
        "role": "student"
    }
    
    print(f"Testing registration with email: {test_email}")
    
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
            
            # Parse the response to verify user was created
            try:
                user_data = json.loads(result)
                if 'id' in user_data and 'email' in user_data:
                    print(f"✅ User created with ID: {user_data['id']}")
                    print(f"✅ User email: {user_data['email']}")
                    print(f"✅ User role: {user_data['role']}")
                    return True, test_email
                else:
                    print("⚠️  Unexpected response format")
                    return False, None
            except:
                print("⚠️  Could not parse response")
                return False, None
            
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
        return False, None
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False, None

def test_login_with_new_user(email):
    """Test login with the newly created user"""
    print("\n🚀 TESTING LOGIN WITH NEW USER")
    print("=" * 40)
    
    # Use the email from registration
    test_email = email
    
    login_data = {
        "email": test_email,
        "password": "testpassword123"
    }
    
    print(f"Testing login with email: {test_email}")
    
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
                else:
                    print("⚠️  No access token in response")
                    return False
            except:
                print("⚠️  Could not parse token from response")
                return False
            
    except urllib.error.HTTPError as e:
        result = e.read().decode('utf-8')
        print(f"📋 Login response:")
        print(f"   Status: {e.code}")
        print(f"   Response: {result}")
        
        if e.code == 401:
            print("❌ Login failed - incorrect email or password")
        elif e.code == 422:
            print("❌ Login failed - invalid data format")
        else:
            print("❌ Unexpected error")
        return False
        
    except Exception as e:
        print(f"❌ Connection error: {e}")
        return False

if __name__ == "__main__":
    print("🔧 TUTORAPP NEW USER TEST")
    print("=" * 50)
    
    # Test registration first
    registration_ok, test_email = test_new_registration()
    
    if registration_ok:
        # Test login with the new user
        login_ok = test_login_with_new_user(test_email)
        
        print(f"\n{'='*50}")
        print("📊 TEST SUMMARY")
        print(f"{'='*50}")
        
        if registration_ok:
            print("✅ Registration: Working")
        else:
            print("❌ Registration: Failed")
            
        if login_ok:
            print("✅ Login: Working")
        else:
            print("❌ Login: Failed")
        
        if registration_ok and login_ok:
            print("\n🎉 SUCCESS! Registration and login are working perfectly!")
            print("✅ Your TutorApp is fully functional!")
        else:
            print("\n⚠️  Some issues detected")
    else:
        print("\n❌ Registration failed - cannot test login")
    
    print(f"\n🌐 Visit: https://tutorapp-production.up.railway.app")
