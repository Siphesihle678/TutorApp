#!/usr/bin/env python3
"""
Debug Endpoints
Debug specific endpoint issues
"""

import urllib.request
import urllib.parse
import json
import ssl

# Disable SSL verification for testing
ssl._create_default_https_context = ssl._create_unverified_context

RAILWAY_URL = "https://tutorapp-production.up.railway.app"

def debug_endpoint(url, method="GET", data=None):
    """Debug an endpoint and show detailed response"""
    try:
        if data:
            data = json.dumps(data).encode('utf-8')
            req = urllib.request.Request(url, data=data, method=method)
            req.add_header('Content-Type', 'application/json')
        else:
            req = urllib.request.Request(url, method=method)
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = response.read().decode('utf-8')
            print(f"✅ SUCCESS: {response.status}")
            print(f"   Response: {result}")
            return True
            
    except urllib.error.HTTPError as e:
        result = e.read().decode('utf-8')
        print(f"❌ HTTP ERROR: {e.code}")
        print(f"   Response: {result}")
        return False
        
    except Exception as e:
        print(f"❌ EXCEPTION: {str(e)}")
        return False

def main():
    """Debug specific endpoints"""
    print("🔍 DEBUGGING ENDPOINTS")
    print("=" * 50)
    
    endpoints = [
        ("Dashboard Stats", f"{RAILWAY_URL}/api/dashboard/stats"),
        ("Public Quizzes", f"{RAILWAY_URL}/api/quizzes/public"),
        ("Public Assignments", f"{RAILWAY_URL}/api/assignments/public"),
        ("Public Announcements", f"{RAILWAY_URL}/api/announcements/public"),
        ("Dashboard Test", f"{RAILWAY_URL}/api/dashboard/test"),
        ("Auth Test", f"{RAILWAY_URL}/api/auth/test-auth"),
    ]
    
    for name, url in endpoints:
        print(f"\n🔍 Testing: {name}")
        print(f"   URL: {url}")
        debug_endpoint(url)
        print("-" * 30)

if __name__ == "__main__":
    main()
