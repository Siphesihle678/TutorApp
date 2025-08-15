#!/usr/bin/env python3
"""
Delete All Users Script
Safely removes all users from the TutorApp database
"""

import urllib.request
import urllib.parse
import json
import ssl

# Disable SSL verification for testing
ssl._create_default_https_context = ssl._create_unverified_context

RAILWAY_URL = "https://tutorapp-production.up.railway.app"

def delete_all_users():
    """Delete all users from the database"""
    print("🗑️  DELETING ALL USERS")
    print("=" * 50)
    
    # First, let's check current users
    print("📊 Current Users:")
    try:
        # Get dashboard stats to see current user count
        req = urllib.request.Request(f"{RAILWAY_URL}/api/dashboard/stats")
        with urllib.request.urlopen(req, timeout=10) as response:
            stats_data = json.loads(response.read().decode('utf-8'))
            users = stats_data.get('stats', {}).get('users', {})
            total_users = users.get('total', 0)
            students = users.get('students', 0)
            teachers = users.get('teachers', 0)
            
            print(f"   Total Users: {total_users}")
            print(f"   Students: {students}")
            print(f"   Teachers: {teachers}")
    except Exception as e:
        print(f"   ❌ Could not get current user count: {e}")
        return False
    
    # Confirm deletion
    print(f"\n⚠️  WARNING: This will delete ALL {total_users} users!")
    print("   This action cannot be undone.")
    print("   Are you sure you want to continue? (yes/no)")
    
    # For safety, we'll use a simple confirmation
    # In a real scenario, you might want to add more confirmation
    confirmation = input("   Enter 'DELETE_ALL_USERS' to confirm: ")
    
    if confirmation != "DELETE_ALL_USERS":
        print("❌ Deletion cancelled.")
        return False
    
    print("\n🗑️  Proceeding with user deletion...")
    
    # Create a migration endpoint to delete all users
    # We'll need to add this endpoint to the migration router
    try:
        # Call the delete all users endpoint
        req = urllib.request.Request(
            f"{RAILWAY_URL}/api/migration/delete-all-users",
            method="DELETE"
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
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

def verify_deletion():
    """Verify that all users have been deleted"""
    print("\n🔍 Verifying deletion...")
    
    try:
        req = urllib.request.Request(f"{RAILWAY_URL}/api/dashboard/stats")
        with urllib.request.urlopen(req, timeout=10) as response:
            stats_data = json.loads(response.read().decode('utf-8'))
            users = stats_data.get('stats', {}).get('users', {})
            total_users = users.get('total', 0)
            
            if total_users == 0:
                print("✅ SUCCESS: All users have been deleted!")
                return True
            else:
                print(f"❌ FAILED: {total_users} users still remain")
                return False
                
    except Exception as e:
        print(f"❌ Could not verify deletion: {e}")
        return False

def main():
    """Main function"""
    print("🚀 TUTORAPP USER DELETION TOOL")
    print("=" * 50)
    
    # Delete all users
    success = delete_all_users()
    
    if success:
        # Verify deletion
        verify_deletion()
    
    print(f"\n{'='*50}")
    print("🏁 DELETION PROCESS COMPLETE")
    print(f"{'='*50}")

if __name__ == "__main__":
    main()
