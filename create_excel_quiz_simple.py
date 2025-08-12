#!/usr/bin/env python3
"""
Excel Quiz Creator for TutorApp - Simple Version
Uses built-in Python libraries instead of requests
"""

import urllib.request
import urllib.parse
import json

# Your Railway URL
RAILWAY_URL = "https://tutorapp-production.up.railway.app"

def create_excel_quiz():
    """Create the Excel quiz via API using built-in libraries"""
    
    # First, login as teacher to get token
    login_data = {
        "email": "teacher@example.com",
        "password": "password123"
    }
    
    try:
        # Login
        login_url = f"{RAILWAY_URL}/api/auth/login"
        login_json = json.dumps(login_data).encode('utf-8')
        
        login_req = urllib.request.Request(
            login_url,
            data=login_json,
            headers={'Content-Type': 'application/json'}
        )
        
        with urllib.request.urlopen(login_req) as response:
            if response.status != 200:
                print("❌ Login failed. Please create a teacher account first.")
                print("Go to your app and register as a teacher with email: teacher@example.com")
                return
            
            token_data = json.loads(response.read().decode('utf-8'))
            token = token_data["access_token"]
        
        # Excel Quiz data based on the user's HTML example
        quiz_data = {
            "title": "Excel — Student Marks Analysis (Auto-graded)",
            "description": "Answer the questions based on the concepts covered in the lesson, not the activity steps. Test your knowledge of Excel functions and formulas.",
            "subject": "CAT",
            "time_limit": 45,  # 45 minutes for 9 questions
            "passing_score": 60.0,
            "questions": [
                {
                    "text": "What does the SUM function do in Excel?",
                    "question_type": "text",
                    "correct_answer": "It adds up the numbers in the selected cells.",
                    "points": 1.0,
                    "explanation": "The SUM function calculates the total of all numbers in a specified range of cells."
                },
                {
                    "text": "Write the formula to calculate the average of cells D2 to F2.",
                    "question_type": "text",
                    "correct_answer": "=AVERAGE(D2:F2)",
                    "points": 1.0,
                    "explanation": "The AVERAGE function calculates the arithmetic mean of the specified range."
                },
                {
                    "text": "How would you use IF to display \"Pass\" if a score in H2 is 50 or more, otherwise \"Fail\"?",
                    "question_type": "text",
                    "correct_answer": "=IF(H2>=50,\"Pass\",\"Fail\")",
                    "points": 1.0,
                    "explanation": "The IF function tests a condition and returns one value if true, another if false."
                },
                {
                    "text": "Explain what a nested IF formula is used for.",
                    "question_type": "text",
                    "correct_answer": "A formula that uses multiple IF statements inside each other to test several conditions.",
                    "points": 1.0,
                    "explanation": "Nested IF statements allow you to test multiple conditions in a single formula."
                },
                {
                    "text": "Which function would you use to find the highest score in a column?",
                    "question_type": "text",
                    "correct_answer": "=MAX(column_range)",
                    "points": 1.0,
                    "explanation": "The MAX function returns the largest value in a set of values."
                },
                {
                    "text": "Describe how COUNTIF works and give one example.",
                    "question_type": "text",
                    "correct_answer": "Counts the number of cells that meet a condition, e.g., =COUNTIF(A1:A10,\">50\")",
                    "points": 1.0,
                    "explanation": "COUNTIF counts cells that meet a specified criterion within a range."
                },
                {
                    "text": "What does CONCATENATE do?",
                    "question_type": "text",
                    "correct_answer": "Combines text from two or more cells into one.",
                    "points": 1.0,
                    "explanation": "CONCATENATE joins multiple text strings into one text string."
                },
                {
                    "text": "Which function can retrieve data from another table based on a matching value?",
                    "question_type": "text",
                    "correct_answer": "VLOOKUP",
                    "points": 1.0,
                    "explanation": "VLOOKUP searches for a value in the first column of a table and returns a value from the same row in another column."
                },
                {
                    "text": "How would you highlight all scores below 40 using Conditional Formatting?",
                    "question_type": "text",
                    "correct_answer": "Select the cells → Conditional Formatting → New Rule → Cell Value < 40 → Apply formatting.",
                    "points": 1.0,
                    "explanation": "Conditional Formatting allows you to automatically format cells based on their values."
                }
            ]
        }
        
        # Create quiz
        quiz_url = f"{RAILWAY_URL}/api/quizzes/"
        quiz_json = json.dumps(quiz_data).encode('utf-8')
        
        quiz_req = urllib.request.Request(
            quiz_url,
            data=quiz_json,
            headers={
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {token}'
            }
        )
        
        with urllib.request.urlopen(quiz_req) as response:
            if response.status == 200:
                print("✅ Excel quiz created successfully!")
                print("📊 Quiz: Excel — Student Marks Analysis (Auto-graded)")
                print("📝 Questions: 9 text-based questions")
                print("⏱️ Time Limit: 45 minutes")
                print("🎯 Passing Score: 60%")
                print("\n📋 Question Types:")
                print("   • Text-based answers (not multiple choice)")
                print("   • Students type their responses")
                print("   • Auto-graded based on exact text matching")
                print("\n🚀 You can now test the quiz with a student account!")
            else:
                print(f"❌ Error creating quiz: {response.read().decode('utf-8')}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure your app is running and accessible at the URL above.")

if __name__ == "__main__":
    print("🎯 Creating Excel quiz for CAT Grade 11...")
    print("⚠️  Make sure you have a teacher account on your app first!")
    create_excel_quiz()
