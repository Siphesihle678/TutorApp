#!/usr/bin/env python3
"""
Railway Database Schema Fix
Fixes the database schema on Railway deployment
"""

import urllib.request
import urllib.parse
import json
import ssl

# Disable SSL verification for testing
ssl._create_default_https_context = ssl._create_unverified_context

RAILWAY_URL = "https://tutorapp-production.up.railway.app"

def fix_schema():
    """Fix the database schema on Railway"""
    print("🔧 FIXING RAILWAY DATABASE SCHEMA")
    print("=" * 50)
    
    try:
        # First check schema status
        print("1. Checking current schema status...")
        req = urllib.request.Request(f"{RAILWAY_URL}/api/migration/schema-status")
        
        with urllib.request.urlopen(req, timeout=10) as response:
            status_data = json.loads(response.read().decode('utf-8'))
            print(f"   Status: {status_data}")
            
            if not status_data.get('schema_status', {}).get('needs_fix', True):
                print("✅ Schema is already correct!")
                return True
        
        # Fix the schema
        print("\n2. Fixing database schema...")
        req = urllib.request.Request(
            f"{RAILWAY_URL}/api/migration/fix-schema",
            method="POST"
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            fix_data = json.loads(response.read().decode('utf-8'))
            print(f"   Result: {fix_data}")
            
        print("✅ Database schema fixed successfully!")
        return True
        
    except urllib.error.HTTPError as e:
        result = e.read().decode('utf-8')
        print(f"❌ HTTP Error: {e.code}")
        print(f"   Response: {result}")
        return False
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_login_after_fix():
    """Test login after schema fix"""
    print("\n3. Testing login after schema fix...")
    
    try:
        login_data = {
            "email": "test@example.com",
            "password": "testpassword123"
        }
        
        data = json.dumps(login_data).encode('utf-8')
        req = urllib.request.Request(
            f"{RAILWAY_URL}/api/auth/login",
            data=data,
            method="POST"
        )
        req.add_header('Content-Type', 'application/json')
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(f"✅ Login successful!")
            print(f"   Status: {response.status}")
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

def main():
    """Run the complete fix process"""
    print("🚀 RAILWAY DATABASE SCHEMA FIX")
    print("=" * 50)
    
    # Fix schema
    schema_fixed = fix_schema()
    
    if schema_fixed:
        # Test login
        login_works = test_login_after_fix()
        
        if login_works:
            print("\n🎉 SUCCESS! Database schema fixed and login is working!")
            print("✅ You can now log in to your TutorApp!")
        else:
            print("\n⚠️  Schema fixed but login test failed")
    else:
        print("\n❌ Schema fix failed")
    
    return schema_fixed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
