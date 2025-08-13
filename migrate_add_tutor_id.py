#!/usr/bin/env python3
"""
Database migration script to add tutor_id column to users table.
This script should be run once to update the existing database schema.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import DATABASE_URL

def migrate_add_tutor_columns():
    """Add tutor_id and tutor_code columns to users table"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        try:
            # Check if tutor_id column already exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'tutor_id'
            """))
            
            if not result.fetchone():
                # Add tutor_id column
                connection.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN tutor_id INTEGER
                """))
                
                # Create index on tutor_id for better performance
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_users_tutor_id 
                    ON users (tutor_id)
                """))
                
                # Add foreign key constraint
                connection.execute(text("""
                    ALTER TABLE users 
                    ADD CONSTRAINT fk_users_tutor_id 
                    FOREIGN KEY (tutor_id) REFERENCES users (id)
                """))
                
                print("✅ Successfully added tutor_id column to users table")
                print("✅ Created index on tutor_id")
                print("✅ Added foreign key constraint")
            else:
                print("✅ tutor_id column already exists in users table")
            
            # Check if tutor_code column already exists
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'tutor_code'
            """))
            
            if not result.fetchone():
                # Add tutor_code column
                connection.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN tutor_code VARCHAR(10) UNIQUE
                """))
                
                # Create index on tutor_code for better performance
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_users_tutor_code 
                    ON users (tutor_code)
                """))
                
                print("✅ Successfully added tutor_code column to users table")
                print("✅ Created index on tutor_code")
            else:
                print("✅ tutor_code column already exists in users table")
            
            connection.commit()
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            connection.rollback()
            raise

def assign_tutor_codes():
    """Assign tutor codes to existing teachers"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        try:
            # Get teachers without tutor codes
            teachers_without_codes = db.execute(text("""
                SELECT id, name, email 
                FROM users 
                WHERE role = 'teacher' AND tutor_code IS NULL AND is_active = true
            """)).fetchall()
            
            if not teachers_without_codes:
                print("✅ All teachers already have tutor codes")
                return
            
            # Import the utility function
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            from app.core.utils import generate_unique_tutor_code
            
            assigned_count = 0
            for teacher in teachers_without_codes:
                try:
                    # Generate unique tutor code
                    tutor_code = generate_unique_tutor_code(db)
                    
                    # Update teacher with tutor code
                    db.execute(text("""
                        UPDATE users 
                        SET tutor_code = :tutor_code 
                        WHERE id = :teacher_id
                    """), {"tutor_code": tutor_code, "teacher_id": teacher.id})
                    
                    assigned_count += 1
                    print(f"✅ Assigned tutor code '{tutor_code}' to teacher: {teacher.name} ({teacher.email})")
                    
                except Exception as e:
                    print(f"❌ Error assigning tutor code to {teacher.name}: {e}")
                    continue
            
            db.commit()
            print(f"✅ Successfully assigned tutor codes to {assigned_count} teachers")
            
        except Exception as e:
            print(f"❌ Error assigning tutor codes: {e}")
            db.rollback()
            raise

def assign_default_tutor():
    """Assign existing students to the first available teacher"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        try:
            # Get the first teacher
            teacher = db.execute(text("""
                SELECT id, name, email 
                FROM users 
                WHERE role = 'teacher' AND is_active = true 
                LIMIT 1
            """)).fetchone()
            
            if not teacher:
                print("⚠️  No active teachers found. Students will remain unassigned.")
                return
            
            # Count unassigned students
            unassigned_count = db.execute(text("""
                SELECT COUNT(*) 
                FROM users 
                WHERE role = 'student' AND tutor_id IS NULL AND is_active = true
            """)).fetchone()[0]
            
            if unassigned_count == 0:
                print("✅ All students are already assigned to tutors")
                return
            
            # Assign unassigned students to the first teacher
            result = db.execute(text("""
                UPDATE users 
                SET tutor_id = :teacher_id 
                WHERE role = 'student' AND tutor_id IS NULL AND is_active = true
            """), {"teacher_id": teacher.id})
            
            db.commit()
            
            print(f"✅ Assigned {result.rowcount} students to teacher: {teacher.name} ({teacher.email})")
            
        except Exception as e:
            print(f"❌ Error assigning default tutor: {e}")
            db.rollback()
            raise

if __name__ == "__main__":
    print("🚀 Starting database migration for tutor-student linking...")
    
    try:
        migrate_add_tutor_columns()
        assign_tutor_codes()
        assign_default_tutor()
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"💥 Migration failed: {e}")
        sys.exit(1)
