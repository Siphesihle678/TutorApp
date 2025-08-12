#!/usr/bin/env python3
"""
Test script to verify the app can start and respond to health checks
"""
import sys
import os
from pathlib import Path

# Add the current directory to Python path
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

def test_app_startup():
    """Test if the app can start without database dependencies"""
    try:
        # Import the app
        from main import app
        print("✅ App imported successfully")
        
        # Test health check endpoint
        from fastapi.testclient import TestClient
        client = TestClient(app)
        
        # Test root endpoint
        response = client.get("/")
        print(f"✅ Root endpoint: {response.status_code}")
        
        # Test health endpoint
        response = client.get("/health")
        print(f"✅ Health endpoint: {response.status_code}")
        print(f"   Response: {response.json()}")
        
        return True
        
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing TutorApp startup...")
    success = test_app_startup()
    if success:
        print("🎉 App test passed!")
    else:
        print("💥 App test failed!")
        sys.exit(1)
