import json
import random
import os
from google import genai
from google.genai import types

# Configure Gemini (it will warn if key is invalid when called, not on import)
_gemini_key = os.environ.get("GEMINI_API_KEY", "")

class TutorAIAssistant:
    """Fully functional AI wrapper leveraging Google Gemini 2.5 Flash."""
    
    def __init__(self):
        # We use Flash by default as it is fast and heavily suitable for JSON/text tasks
        self.client = genai.Client(api_key=_gemini_key) if _gemini_key else None
        self.model_name = 'gemini-2.5-flash'
    
    def grade_text_answer(self, question_text: str, student_answer: str, max_points: float) -> dict:
        """Dynamically grade student answers."""
        if not _gemini_key:
            # Fallback mock
            deduction = random.uniform(0, max_points * 0.2)
            return {"ai_suggested_score": round(max(0, max_points - deduction), 1), "ai_feedback": "Mock Feedback: Provide API Key for real AI generation."}
            
        prompt = f"""
        You are a strict but fair academic tutor grading an exam.
        Question: {question_text}
        Student Answer: {student_answer}
        Maximum Points: {max_points}
        
        Analyze the student's answer. Output ONLY a valid JSON object with the following keys:
        - "ai_suggested_score": a float representing the score they deserve (max {max_points})
        - "ai_feedback": a very short 1-2 sentence constructive feedback.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            print(f"Gemini API Error: {e}")
            return {"ai_suggested_score": max_points, "ai_feedback": "Error generating AI response. Defaulting to full score."}
        
    def generate_study_plan(self, topic: str, duration_weeks: int) -> str:
        """Returns a bespoke markdown study plan."""
        if not _gemini_key:
            return f"### Mock {duration_weeks}-Week Study Plan for {topic}\n*(Please add GEMINI_API_KEY to your .env file to see the real AI magic!)*"
            
        prompt = f"Act as an expert curriculum designer. Generate a highly structured, engaging {duration_weeks}-week study plan markdown document for the topic: '{topic}'. Do not include introductory conversational text, just output exactly the markdown."
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return response.text
        except Exception as e:
            return f"**Error generating plan:** {str(e)}"

    def synthesize_unique_dataset(self, scenario_type: str) -> dict:
        """Mathematically synthesize unique structural JSON for database/excel teaching."""
        if not _gemini_key:
            uid = random.randint(1000, 9999)
            return {"file_type": "mock_csv", "table_name": f"Mock_{uid}", "columns": ["ID", "Val"], "data": [["1", "A"]], "generator_message": "Mock dataset. Add API key."}
            
        prompt = f"""
        Generate a teaching scenario dataset for a '{scenario_type}' lesson.
        Output ONLY a valid JSON object matching this exact schema:
        {{
            "file_type": "csv_representing_table",
            "table_name": "AppropriateTableName",
            "columns": ["Col1", "Col2", "Col3"],
            "data": [
                ["Row1Val1", "Row1Val2", "Row1Val3"],
                ["Row2Val1", "Row2Val2", "Row2Val3"]
            ],
            "generator_message": "A short 1 sentence message explaining the scenario."
        }}
        Provide randomly invented, highly realistic data with 4-5 columns and exactly 5 items.
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            return {"error": f"Failed to generate dataset: {str(e)}"}
            
    def generate_quiz_from_content(self, content: str) -> dict:
        """Parses raw text content and spits out an editable JSON quiz schema."""
        if not _gemini_key:
            return {"title": "Mock API Key Quiz", "description": "You need to add GEMINI_API_KEY to your .env file.", "questions": []}
            
        prompt = f"""
        You are an expert test creator. Here is raw study material provided by a teacher:
        START MATERIAL
        {content}
        END MATERIAL
        
        Generate a beautiful, engaging quiz based STRICTLY on the content provided. 
        Create exactly 5 questions (mix of "multiple_choice", "true_false", and "short_answer").
        
        Output ONLY a valid JSON object adhering to this schema:
        {{
            "title": "A catchy title summarizing the content",
            "description": "A short 1 sentence description",
            "questions": [
                {{
                    "text": "The question text",
                    "question_type": "multiple_choice",
                    "options": ["A", "B", "C", "D"], // Only for multiple_choice, otherwise empty array []
                    "correct_answer": "The exact correct option string (e.g. 'A' or 'True' or 'The specific short answer keyword')",
                    "points": 1.0,
                    "explanation": "A very short explanation of why this is correct."
                }}
            ]
        }}
        """
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt,
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            return json.loads(response.text)
        except Exception as e:
            return {"title": "API Error", "description": str(e), "questions": []}

    def generate_quiz_from_file(self, file_path: str) -> dict:
        """Uploads a file to Gemini, generates a quiz from it, and cleans up the file."""
        if not _gemini_key:
            return {"title": "Mock API Key Quiz", "description": "You need to add GEMINI_API_KEY to your .env file.", "questions": []}
            
        try:
            # Upload the file to Gemini
            uploaded_file = self.client.files.upload(file=file_path)
            
            prompt = """
            You are an expert test creator. Here is raw study material provided by a teacher in the attached document.
            
            Generate a beautiful, engaging quiz based STRICTLY on the content provided in the file. 
            Create exactly 5 questions (mix of "multiple_choice", "true_false", and "short_answer").
            
            Output ONLY a valid JSON object adhering to this schema:
            {
                "title": "A catchy title summarizing the content",
                "description": "A short 1 sentence description",
                "questions": [
                    {
                        "text": "The question text",
                        "question_type": "multiple_choice",
                        "options": ["A", "B", "C", "D"], // Only for multiple_choice, otherwise empty array []
                        "correct_answer": "The exact correct option string (e.g. 'A' or 'True' or 'The specific short answer keyword')",
                        "points": 1.0,
                        "explanation": "A very short explanation of why this is correct."
                    }
                ]
            }
            """
            
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[uploaded_file, prompt],
                config=types.GenerateContentConfig(response_mime_type="application/json")
            )
            
            # Cleanup the file from Gemini
            try:
                self.client.files.delete(name=uploaded_file.name)
            except Exception as e:
                print(f"Warning: Failed to delete file {uploaded_file.name} from Gemini: {e}")
                
            return json.loads(response.text)
            
        except Exception as e:
            return {"title": "API Error", "description": str(e), "questions": []}

ai_assistant = TutorAIAssistant()
