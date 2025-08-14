#!/usr/bin/env python3
"""
Database Schema Fix Script
Adds missing columns to the database schema
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

def fix_database_schema():
    """Fix the database schema by adding missing columns"""
    print("🔧 FIXING DATABASE SCHEMA")
    print("=" * 50)
    
    try:
        from app.core.database import engine
        from sqlalchemy import text
        
        # Check if tutor_id column exists
        with engine.connect() as conn:
            # Check if tutor_id column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'tutor_id'
            """))
            
            if result.fetchone():
                print("✅ tutor_id column already exists")
            else:
                print("❌ tutor_id column missing - adding it...")
                
                # Add the tutor_id column
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN tutor_id INTEGER,
                    ADD CONSTRAINT fk_users_tutor_id 
                    FOREIGN KEY (tutor_id) REFERENCES users(id)
                """))
                
                # Create index on tutor_id
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_users_tutor_id 
                    ON users(tutor_id)
                """))
                
                print("✅ tutor_id column added successfully")
            
            # Check if tutor_code column exists
            result = conn.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'tutor_code'
            """))
            
            if result.fetchone():
                print("✅ tutor_code column already exists")
            else:
                print("❌ tutor_code column missing - adding it...")
                
                # Add the tutor_code column
                conn.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN tutor_code VARCHAR,
                    ADD CONSTRAINT uq_users_tutor_code UNIQUE (tutor_code)
                """))
                
                # Create index on tutor_code
                conn.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_users_tutor_code 
                    ON users(tutor_code)
                """))
                
                print("✅ tutor_code column added successfully")
            
            # Commit the changes
            conn.commit()
            print("✅ Database schema updated successfully")
            
        return True
        
    except Exception as e:
        print(f"❌ Database schema fix failed: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return False

def test_database_connection():
    """Test database connection after schema fix"""
    print("\n🔍 TESTING DATABASE CONNECTION")
    print("=" * 50)
    
    try:
        from app.core.database import engine
        from app.models.user import User
        from sqlalchemy import text
        
        # Test basic connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Database connection successful")
            
            # Test User model query
            result = conn.execute(text("SELECT COUNT(*) FROM users"))
            user_count = result.fetchone()[0]
            print(f"✅ User table accessible - {user_count} users found")
            
            # Test if tutor_id column is accessible
            result = conn.execute(text("SELECT tutor_id FROM users LIMIT 1"))
            print("✅ tutor_id column accessible")
            
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def main():
    """Run database schema fix"""
    print("🚀 DATABASE SCHEMA FIX")
    print("=" * 50)
    
    # Fix schema
    schema_fixed = fix_database_schema()
    
    if schema_fixed:
        # Test connection
        connection_ok = test_database_connection()
        
        if connection_ok:
            print("\n🎉 DATABASE SCHEMA FIX COMPLETED SUCCESSFULLY!")
            print("✅ Login should now work properly")
        else:
            print("\n⚠️  Schema fixed but connection test failed")
    else:
        print("\n❌ Database schema fix failed")
    
    return schema_fixed

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
