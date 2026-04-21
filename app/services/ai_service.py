import json
import random

class TutorAIAssistant:
    """Mock AI wrapper. Swap these out with actual openai or google.generativeai logic later."""
    
    @staticmethod
    def grade_text_answer(question_text: str, student_answer: str, max_points: float) -> dict:
        """Mocks reading the student's text structure and giving a score."""
        deduction = random.uniform(0, max_points * 0.2) # Max 20% deduction in mock
        score = max(0, max_points - deduction)
        return {
            "ai_suggested_score": round(score, 1),
            "ai_feedback": "The reasoning is generally solid but lacks a minor technical detail. AI Suggestion: Mention integrity constraints."
        }
        
    @staticmethod
    def generate_study_plan(topic: str, duration_weeks: int) -> str:
        """Returns a generic markdown study plan based on a topic string."""
        return f"### {duration_weeks}-Week Study Plan for {topic}\n\n- **Week 1:** Introduction and Fundamentals\n- **Week 2:** Core Application\n- **Week 3:** Complex Formulas/Queries\n- **Week 4:** Final Mock Exam Integration"

    @staticmethod
    def synthesize_unique_dataset(scenario_type: str) -> dict:
        """Solves the 'same data file over and over' request by mathematically synthesizing unique CSV metadata."""
        uid = random.randint(1000, 9999)
        if "database" in scenario_type.lower() or "access" in scenario_type.lower():
            return {
                "file_type": "csv_representing_table",
                "table_name": f"Tbl_{uid}_Customers",
                "columns": ["CustomerID", "FullName", "SubscriptionLevel", "MonthlyFee"],
                "data": [
                    [f"CUST{uid}1", "Alice Johnson", "Premium", "450.00"],
                    [f"CUST{uid}2", "Bob Smith", "Basic", "150.00"],
                    [f"CUST{uid}3", "Charlie Davis", "Pro", "299.99"]
                ],
                "generator_message": f"Unique Random Scenario '{uid}' created. You can cast this to an Access file."
            }
        elif "excel" in scenario_type.lower():
            return {
                "file_type": "csv_representing_spreadsheet",
                "sheet_name": f"Data_{uid}",
                "columns": ["Item", "CostPrice", "SellingPrice", "Markup"],
                "data": [
                    ["Product A", "10", "15", "=C2-B2"],
                    ["Product B", "20", "45", "=C3-B3"]
                ],
                "generator_message": "Unique VLOOKUP/Markup scenario generated."
            }
        return {"error": "Scenario type not recognized. Valid inputs: 'database', 'excel'"}

ai_assistant = TutorAIAssistant()
