#!/usr/bin/env python3
"""
Sample Data Seeder for TutorApp
Creates sample CAT Grade 11 questions and quiz for immediate use
"""

import sys
import os
from pathlib import Path

# Add the current directory to Python path
sys.path.append(str(Path(__file__).parent))

from app.core.database import SessionLocal, engine
from app.models.user import User, UserRole
from app.models.quiz import Quiz, Question, QuestionType
from app.models.assignment import Assignment
from app.core.security import get_password_hash
from datetime import datetime, timedelta

def seed_sample_data():
    """Seed sample data for immediate use"""
    db = SessionLocal()
    
    try:
        # Create sample teacher
        teacher = User(
            name="Sample Teacher",
            email="teacher@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.TEACHER,
            is_active=True
        )
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
        
        # Create sample student
        student = User(
            name="Sample Student",
            email="student@example.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.STUDENT,
            is_active=True
        )
        db.add(student)
        db.commit()
        db.refresh(student)
        
        # Create sample CAT Grade 11 quiz
        quiz = Quiz(
            title="CAT Grade 11 - Excel Basics Quiz",
            description="Test your knowledge of Microsoft Excel fundamentals including formulas, functions, and data formatting.",
            subject="CAT",
            time_limit=30,  # 30 minutes
            passing_score=60.0,
            creator_id=teacher.id,
            is_active=True
        )
        db.add(quiz)
        db.commit()
        db.refresh(quiz)
        
        # Sample CAT Grade 11 questions
        questions = [
            {
                "text": "Which Excel function is used to calculate the average of a range of cells?",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "options": ["SUM()", "AVERAGE()", "COUNT()", "MAX()"],
                "correct_answer": "AVERAGE()",
                "points": 1.0,
                "explanation": "The AVERAGE() function calculates the arithmetic mean of a range of cells."
            },
            {
                "text": "What is the correct syntax for the IF function in Excel?",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "options": ["IF(condition, value_if_true, value_if_false)", "IF(condition, value_if_false, value_if_true)", "IF(value_if_true, condition, value_if_false)", "IF(value_if_false, value_if_true, condition)"],
                "correct_answer": "IF(condition, value_if_true, value_if_false)",
                "points": 1.0,
                "explanation": "The IF function syntax is: IF(logical_test, value_if_true, value_if_false)"
            },
            {
                "text": "Which keyboard shortcut is used to save a workbook in Excel?",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "options": ["Ctrl+S", "Ctrl+N", "Ctrl+O", "Ctrl+P"],
                "correct_answer": "Ctrl+S",
                "points": 1.0,
                "explanation": "Ctrl+S is the standard keyboard shortcut for saving files in most applications."
            },
            {
                "text": "What does the COUNTIFS function do in Excel?",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "options": ["Counts cells that meet multiple criteria", "Counts all cells in a range", "Counts only text cells", "Counts only numeric cells"],
                "correct_answer": "Counts cells that meet multiple criteria",
                "points": 1.0,
                "explanation": "COUNTIFS counts the number of cells that meet multiple specified criteria."
            },
            {
                "text": "How do you create a chart in Excel?",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "options": ["Select data and press F11", "Select data and press Ctrl+Shift+F", "Select data and go to Insert > Chart", "Select data and press Alt+C"],
                "correct_answer": "Select data and go to Insert > Chart",
                "points": 1.0,
                "explanation": "To create a chart, select your data and go to the Insert tab, then choose the desired chart type."
            },
            {
                "text": "What is the purpose of the VLOOKUP function?",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "options": ["To look up values vertically in a table", "To look up values horizontally in a table", "To validate data entry", "To format cells"],
                "correct_answer": "To look up values vertically in a table",
                "points": 1.0,
                "explanation": "VLOOKUP searches for a value in the first column of a table and returns a value from the same row in another column."
            },
            {
                "text": "Which formatting option is used to display numbers as currency?",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "options": ["General", "Currency", "Percentage", "Text"],
                "correct_answer": "Currency",
                "points": 1.0,
                "explanation": "The Currency format displays numbers with a currency symbol and appropriate decimal places."
            },
            {
                "text": "What is the maximum number of rows in a modern Excel worksheet?",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "options": ["65,536", "1,048,576", "2,147,483,647", "Unlimited"],
                "correct_answer": "1,048,576",
                "points": 1.0,
                "explanation": "Modern Excel worksheets can have up to 1,048,576 rows (2^20)."
            },
            {
                "text": "How do you freeze panes in Excel?",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "options": ["View > Freeze Panes", "Home > Freeze Panes", "Insert > Freeze Panes", "Data > Freeze Panes"],
                "correct_answer": "View > Freeze Panes",
                "points": 1.0,
                "explanation": "Freeze Panes is found in the View tab and allows you to keep certain rows or columns visible while scrolling."
            },
            {
                "text": "What is the purpose of the CONCATENATE function?",
                "question_type": QuestionType.MULTIPLE_CHOICE,
                "options": ["To combine text from multiple cells", "To separate text into multiple cells", "To count characters in a cell", "To find text within a cell"],
                "correct_answer": "To combine text from multiple cells",
                "points": 1.0,
                "explanation": "CONCATENATE joins multiple text strings into one text string."
            }
        ]
        
        # Add questions to the quiz
        for q_data in questions:
            question = Question(
                text=q_data["text"],
                question_type=q_data["question_type"],
                options=q_data["options"],
                correct_answer=q_data["correct_answer"],
                points=q_data["points"],
                explanation=q_data["explanation"],
                quiz_id=quiz.id
            )
            db.add(question)
        
        # Create sample assignment
        assignment = Assignment(
            title="CAT Grade 11 - Excel Practical Assignment",
            description="Create a spreadsheet to track student marks and calculate averages, percentages, and grades. Include formulas for automatic calculations and format the data appropriately.",
            subject="CAT",
            max_points=50.0,
            due_date=datetime.utcnow() + timedelta(days=7),  # Due in 7 days
            creator_id=teacher.id,
            is_active=True
        )
        db.add(assignment)
        
        db.commit()
        
        print("✅ Sample data created successfully!")
        print(f"📝 Teacher account: teacher@example.com / password123")
        print(f"👨‍🎓 Student account: student@example.com / password123")
        print(f"📊 Sample quiz: 'CAT Grade 11 - Excel Basics Quiz' with 10 questions")
        print(f"📋 Sample assignment: 'CAT Grade 11 - Excel Practical Assignment'")
        print("\n🚀 You can now log in and test the quiz creation and assignment features!")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_sample_data()
