#!/usr/bin/env python3
"""
Simple script to create a sample quiz for testing
Run this after your app is deployed and you have a teacher account
"""

import requests
import json

# Replace with your actual Railway URL
RAILWAY_URL = "https://your-app-name.railway.app"  # Change this to your actual URL

def create_sample_quiz():
    """Create a sample quiz via API"""
    
    # First, login as teacher to get token
    login_data = {
        "email": "teacher@example.com",
        "password": "password123"
    }
    
    try:
        # Login
        login_response = requests.post(f"{RAILWAY_URL}/api/auth/login", json=login_data)
        if not login_response.ok:
            print("❌ Login failed. Please create a teacher account first.")
            print("Go to your app and register as a teacher with email: teacher@example.com")
            return
        
        token_data = login_response.json()
        token = token_data["access_token"]
        
        # Quiz data
        quiz_data = {
            "title": "CAT Grade 11 - Excel Basics Quiz",
            "description": "Test your knowledge of Microsoft Excel fundamentals including formulas, functions, and data formatting.",
            "subject": "CAT",
            "time_limit": 30,
            "passing_score": 60.0,
            "questions": [
                {
                    "text": "Which Excel function is used to calculate the average of a range of cells?",
                    "question_type": "multiple_choice",
                    "options": ["SUM()", "AVERAGE()", "COUNT()", "MAX()"],
                    "correct_answer": "AVERAGE()",
                    "points": 1.0,
                    "explanation": "The AVERAGE() function calculates the arithmetic mean of a range of cells."
                },
                {
                    "text": "What is the correct syntax for the IF function in Excel?",
                    "question_type": "multiple_choice",
                    "options": [
                        "IF(condition, value_if_true, value_if_false)",
                        "IF(condition, value_if_false, value_if_true)",
                        "IF(value_if_true, condition, value_if_false)",
                        "IF(value_if_false, value_if_true, condition)"
                    ],
                    "correct_answer": "IF(condition, value_if_true, value_if_false)",
                    "points": 1.0,
                    "explanation": "The IF function syntax is: IF(logical_test, value_if_true, value_if_false)"
                },
                {
                    "text": "Which keyboard shortcut is used to save a workbook in Excel?",
                    "question_type": "multiple_choice",
                    "options": ["Ctrl+S", "Ctrl+N", "Ctrl+O", "Ctrl+P"],
                    "correct_answer": "Ctrl+S",
                    "points": 1.0,
                    "explanation": "Ctrl+S is the standard keyboard shortcut for saving files in most applications."
                },
                {
                    "text": "What does the COUNTIFS function do in Excel?",
                    "question_type": "multiple_choice",
                    "options": [
                        "Counts cells that meet multiple criteria",
                        "Counts all cells in a range",
                        "Counts only text cells",
                        "Counts only numeric cells"
                    ],
                    "correct_answer": "Counts cells that meet multiple criteria",
                    "points": 1.0,
                    "explanation": "COUNTIFS counts the number of cells that meet multiple specified criteria."
                },
                {
                    "text": "How do you create a chart in Excel?",
                    "question_type": "multiple_choice",
                    "options": [
                        "Select data and press F11",
                        "Select data and press Ctrl+Shift+F",
                        "Select data and go to Insert > Chart",
                        "Select data and press Alt+C"
                    ],
                    "correct_answer": "Select data and go to Insert > Chart",
                    "points": 1.0,
                    "explanation": "To create a chart, select your data and go to the Insert tab, then choose the desired chart type."
                }
            ]
        }
        
        # Create quiz
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
        
        quiz_response = requests.post(f"{RAILWAY_URL}/api/quizzes/", json=quiz_data, headers=headers)
        
        if quiz_response.ok:
            print("✅ Sample quiz created successfully!")
            print("📊 Quiz: CAT Grade 11 - Excel Basics Quiz")
            print("📝 Questions: 5 multiple choice questions")
            print("⏱️ Time Limit: 30 minutes")
            print("🎯 Passing Score: 60%")
            print("\n🚀 You can now test the quiz with a student account!")
        else:
            print(f"❌ Error creating quiz: {quiz_response.text}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your app is running and accessible at the URL above.")

if __name__ == "__main__":
    print("🎯 Creating sample quiz for CAT Grade 11...")
    print("⚠️  Make sure to update the RAILWAY_URL variable with your actual app URL!")
    create_sample_quiz()
