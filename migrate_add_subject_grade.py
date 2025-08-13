#!/usr/bin/env python3
"""
Database migration script to add subject and grade tables.
This script should be run once to update the existing database schema.
"""

import os
import sys
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Add the app directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.database import DATABASE_URL

def migrate_add_subject_grade_tables():
    """Add subject and grade tables to the database"""
    engine = create_engine(DATABASE_URL)
    
    with engine.connect() as connection:
        try:
            # Check if subjects table already exists
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'subjects'
            """))
            
            if not result.fetchone():
                # Create subjects table
                connection.execute(text("""
                    CREATE TABLE subjects (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR NOT NULL,
                        description TEXT,
                        tutor_id INTEGER NOT NULL REFERENCES users(id),
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ
                    )
                """))
                
                # Create index on tutor_id
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_subjects_tutor_id 
                    ON subjects (tutor_id)
                """))
                
                print("✅ Successfully created subjects table")
            else:
                print("✅ subjects table already exists")
            
            # Check if grades table already exists
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'grades'
            """))
            
            if not result.fetchone():
                # Create grades table
                connection.execute(text("""
                    CREATE TABLE grades (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR NOT NULL,
                        subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
                        is_active BOOLEAN DEFAULT TRUE,
                        created_at TIMESTAMPTZ DEFAULT NOW(),
                        updated_at TIMESTAMPTZ
                    )
                """))
                
                # Create index on subject_id
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_grades_subject_id 
                    ON grades (subject_id)
                """))
                
                print("✅ Successfully created grades table")
            else:
                print("✅ grades table already exists")
            
            # Check if student_grades table already exists
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_name = 'student_grades'
            """))
            
            if not result.fetchone():
                # Create student_grades table
                connection.execute(text("""
                    CREATE TABLE student_grades (
                        id SERIAL PRIMARY KEY,
                        student_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
                        grade_id INTEGER NOT NULL REFERENCES grades(id) ON DELETE CASCADE,
                        enrolled_at TIMESTAMPTZ DEFAULT NOW(),
                        is_active BOOLEAN DEFAULT TRUE,
                        UNIQUE(student_id, grade_id)
                    )
                """))
                
                # Create indexes
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_student_grades_student_id 
                    ON student_grades (student_id)
                """))
                
                connection.execute(text("""
                    CREATE INDEX IF NOT EXISTS ix_student_grades_grade_id 
                    ON student_grades (grade_id)
                """))
                
                print("✅ Successfully created student_grades table")
            else:
                print("✅ student_grades table already exists")
            
            # Add subject_id and grade_id columns to quizzes table if they don't exist
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'quizzes' AND column_name = 'subject_id'
            """))
            
            if not result.fetchone():
                connection.execute(text("""
                    ALTER TABLE quizzes 
                    ADD COLUMN subject_id INTEGER REFERENCES subjects(id)
                """))
                print("✅ Added subject_id column to quizzes table")
            else:
                print("✅ subject_id column already exists in quizzes table")
            
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'quizzes' AND column_name = 'grade_id'
            """))
            
            if not result.fetchone():
                connection.execute(text("""
                    ALTER TABLE quizzes 
                    ADD COLUMN grade_id INTEGER REFERENCES grades(id)
                """))
                print("✅ Added grade_id column to quizzes table")
            else:
                print("✅ grade_id column already exists in quizzes table")
            
            # Add subject_id and grade_id columns to assignments table if they don't exist
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'assignments' AND column_name = 'subject_id'
            """))
            
            if not result.fetchone():
                connection.execute(text("""
                    ALTER TABLE assignments 
                    ADD COLUMN subject_id INTEGER REFERENCES subjects(id)
                """))
                print("✅ Added subject_id column to assignments table")
            else:
                print("✅ subject_id column already exists in assignments table")
            
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'assignments' AND column_name = 'grade_id'
            """))
            
            if not result.fetchone():
                connection.execute(text("""
                    ALTER TABLE assignments 
                    ADD COLUMN grade_id INTEGER REFERENCES grades(id)
                """))
                print("✅ Added grade_id column to assignments table")
            else:
                print("✅ grade_id column already exists in assignments table")
            
            connection.commit()
            
        except Exception as e:
            print(f"❌ Error during migration: {e}")
            connection.rollback()
            raise

def create_default_subjects():
    """Create some default subjects for existing teachers"""
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    with SessionLocal() as db:
        try:
            # Get all teachers
            teachers = db.execute(text("""
                SELECT id, name, email 
                FROM users 
                WHERE role = 'teacher' AND is_active = true
            """)).fetchall()
            
            if not teachers:
                print("⚠️  No active teachers found. No default subjects will be created.")
                return
            
            default_subjects = [
                {"name": "CAT", "description": "Computer Applications Technology"},
                {"name": "Mathematics", "description": "Mathematics"},
                {"name": "English", "description": "English Language"},
                {"name": "Physics", "description": "Physics"},
                {"name": "Accounting", "description": "Accounting"}
            ]
            
            for teacher in teachers:
                print(f"Creating default subjects for teacher: {teacher.name}")
                
                for subject_data in default_subjects:
                    # Check if subject already exists for this teacher
                    existing = db.execute(text("""
                        SELECT id FROM subjects 
                        WHERE tutor_id = :tutor_id AND name = :name
                    """), {"tutor_id": teacher.id, "name": subject_data["name"]}).fetchone()
                    
                    if not existing:
                        # Create subject
                        result = db.execute(text("""
                            INSERT INTO subjects (name, description, tutor_id) 
                            VALUES (:name, :description, :tutor_id) 
                            RETURNING id
                        """), {
                            "name": subject_data["name"],
                            "description": subject_data["description"],
                            "tutor_id": teacher.id
                        })
                        
                        subject_id = result.fetchone()[0]
                        
                        # Create default grades for this subject
                        default_grades = ["Grade 10", "Grade 11", "Grade 12"]
                        for grade_name in default_grades:
                            db.execute(text("""
                                INSERT INTO grades (name, subject_id) 
                                VALUES (:name, :subject_id)
                            """), {"name": grade_name, "subject_id": subject_id})
                        
                        print(f"  ✅ Created subject '{subject_data['name']}' with grades")
                    else:
                        print(f"  ⚠️  Subject '{subject_data['name']}' already exists for {teacher.name}")
                
                db.commit()
            
            print("✅ Default subjects and grades created successfully")
            
        except Exception as e:
            print(f"❌ Error creating default subjects: {e}")
            db.rollback()
            raise

if __name__ == "__main__":
    print("🚀 Starting database migration for subject/grade system...")
    
    try:
        migrate_add_subject_grade_tables()
        create_default_subjects()
        print("🎉 Migration completed successfully!")
        
    except Exception as e:
        print(f"💥 Migration failed: {e}")
        sys.exit(1)
