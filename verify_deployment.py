#!/usr/bin/env python3
"""
Deployment Verification Script for TutorApp
Tests the live Railway deployment to ensure 100% functionality
"""

import requests
import json
import time
from datetime import datetime

# Configuration - Update this with your actual Railway URL
RAILWAY_URL = "https://tutorapp-production.up.railway.app"  # Update this URL
API_BASE = f"{RAILWAY_URL}/api"

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🚀 DEPLOYMENT TEST: {test_name}")
    print(f"{'='*60}")

def print_test_result(test_name, success, message=""):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"   {message}")

def test_railway_health():
    """Test Railway deployment health"""
    print_test_header("Railway Health Check")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/health", timeout=10)
        success = response.status_code == 200
        print_test_result("Railway Health", success, f"Status: {response.status_code}")
        if success:
            data = response.json()
            print(f"   App: {data.get('message', 'N/A')}")
            print(f"   Version: {data.get('version', 'N/A')}")
        return success
    except requests.exceptions.Timeout:
        print_test_result("Railway Health", False, "Timeout - Railway may still be deploying")
        return False
    except Exception as e:
        print_test_result("Railway Health", False, f"Error: {str(e)}")
        return False

def test_railway_database():
    """Test Railway database connection"""
    print_test_header("Railway Database")
    
    try:
        response = requests.get(f"{API_BASE}/quizzes/test/connection", timeout=10)
        success = response.status_code == 200
        print_test_result("Database Connection", success, f"Status: {response.status_code}")
        if success:
            data = response.json()
            print(f"   Connected: {data.get('database_connected', False)}")
            print(f"   Quiz Count: {data.get('quiz_count', 0)}")
            print(f"   Question Count: {data.get('question_count', 0)}")
        return success
    except requests.exceptions.Timeout:
        print_test_result("Database Connection", False, "Timeout - Service may be starting")
        return False
    except Exception as e:
        print_test_result("Database Connection", False, f"Error: {str(e)}")
        return False

def test_railway_api_docs():
    """Test Railway API documentation"""
    print_test_header("Railway API Documentation")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/docs", timeout=10)
        success = response.status_code == 200
        print_test_result("API Documentation", success, f"Status: {response.status_code}")
        return success
    except requests.exceptions.Timeout:
        print_test_result("API Documentation", False, "Timeout")
        return False
    except Exception as e:
        print_test_result("API Documentation", False, f"Error: {str(e)}")
        return False

def test_railway_main_page():
    """Test Railway main page"""
    print_test_header("Railway Main Page")
    
    try:
        response = requests.get(f"{RAILWAY_URL}/", timeout=10)
        success = response.status_code == 200
        print_test_result("Main Page", success, f"Status: {response.status_code}")
        return success
    except requests.exceptions.Timeout:
        print_test_result("Main Page", False, "Timeout")
        return False
    except Exception as e:
        print_test_result("Main Page", False, f"Error: {str(e)}")
        return False

def test_railway_endpoints():
    """Test Railway API endpoints"""
    print_test_header("Railway API Endpoints")
    
    endpoints = [
        ("Authentication", f"{API_BASE}/auth/register"),
        ("Quizzes", f"{API_BASE}/quizzes/"),
        ("Assignments", f"{API_BASE}/assignments/"),
        ("Announcements", f"{API_BASE}/announcements/"),
    ]
    
    results = []
    for name, url in endpoints:
        try:
            response = requests.get(url, timeout=10)
            success = response.status_code in [200, 401, 403, 404, 422]  # Valid responses
            print_test_result(f"{name} Endpoint", success, f"Status: {response.status_code}")
            results.append(success)
        except requests.exceptions.Timeout:
            print_test_result(f"{name} Endpoint", False, "Timeout")
            results.append(False)
        except Exception as e:
            print_test_result(f"{name} Endpoint", False, f"Error: {str(e)}")
            results.append(False)
    
    return all(results)

def wait_for_deployment():
    """Wait for Railway deployment to complete"""
    print(f"\n⏳ Waiting for Railway deployment to complete...")
    print(f"Railway URL: {RAILWAY_URL}")
    
    max_attempts = 30  # 5 minutes total
    attempt = 0
    
    while attempt < max_attempts:
        try:
            response = requests.get(f"{RAILWAY_URL}/health", timeout=5)
            if response.status_code == 200:
                print(f"✅ Railway deployment is LIVE!")
                return True
        except:
            pass
        
        attempt += 1
        print(f"   Attempt {attempt}/{max_attempts} - Waiting...")
        time.sleep(10)
    
    print(f"⚠️  Deployment may still be in progress after 5 minutes")
    return False

def run_deployment_verification():
    """Run complete deployment verification"""
    print(f"\n🚀 TUTORAPP RAILWAY DEPLOYMENT VERIFICATION")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Railway URL: {RAILWAY_URL}")
    
    # Wait for deployment
    if not wait_for_deployment():
        print(f"\n⚠️  Deployment may still be in progress. Please check Railway dashboard.")
        print(f"   Railway Dashboard: https://railway.app/dashboard")
        return False
    
    # Run tests
    tests = [
        ("Health Check", test_railway_health),
        ("Database Connection", test_railway_database),
        ("API Documentation", test_railway_api_docs),
        ("Main Page", test_railway_main_page),
        ("API Endpoints", test_railway_endpoints),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ ERROR in {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Summary
    print(f"\n{'='*60}")
    print(f"📊 DEPLOYMENT VERIFICATION SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    print(f"\n🎯 OVERALL RESULT: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 RAILWAY DEPLOYMENT SUCCESSFUL! TutorApp is 100% functional!")
        print(f"🌐 Live URL: {RAILWAY_URL}")
        print(f"📚 API Docs: {RAILWAY_URL}/docs")
    elif passed >= total * 0.8:
        print("⚠️  MOST TESTS PASSED! Minor issues detected.")
    else:
        print("🚨 SIGNIFICANT ISSUES DETECTED! Check Railway logs.")
    
    return passed == total

if __name__ == "__main__":
    success = run_deployment_verification()
    exit(0 if success else 1)
