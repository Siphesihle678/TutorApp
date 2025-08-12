import openai
import os
from typing import Dict, List, Optional
from datetime import datetime
import json

class TeacherAI:
    def __init__(self):
        """Initialize AI service for teacher efficiency tools"""
        self.api_key = os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
        
        self.client = openai.OpenAI(api_key=self.api_key)
        self.model = "gpt-4"  # or "gpt-3.5-turbo" for cost efficiency
    
    async def get_ai_response(self, prompt: str, system_message: str = None) -> str:
        """Get response from OpenAI API"""
        try:
            messages = []
            
            if system_message:
                messages.append({"role": "system", "content": system_message})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
        except Exception as e:
            return f"AI service error: {str(e)}"
    
    async def generate_quiz(self, subject: str, topic: str, difficulty: str, num_questions: int = 5) -> Dict:
        """Generate quiz questions using AI - TEACHER TOOL"""
        system_message = f"You are an expert {subject} teacher creating assessment materials."
        
        prompt = f"""
        Create a {difficulty} level quiz about {topic} in {subject}.
        
        Requirements:
        - {num_questions} multiple choice questions
        - 4 options per question (A, B, C, D)
        - Include correct answer
        - Include explanation for correct answer
        - Make questions engaging and educational
        - Ensure questions test understanding, not just memorization
        
        Format the response as JSON with this structure:
        {{
            "quiz_title": "Quiz Title",
            "questions": [
                {{
                    "question": "Question text",
                    "options": ["A", "B", "C", "D"],
                    "correct_answer": "A",
                    "explanation": "Explanation of why this is correct"
                }}
            ]
        }}
        """
        
        response = await self.get_ai_response(prompt, system_message)
        
        try:
            quiz_data = json.loads(response)
            return quiz_data
        except json.JSONDecodeError:
            return {
                "quiz_title": f"{subject} Quiz: {topic}",
                "questions": [],
                "raw_response": response
            }
    
    async def grade_assignment(self, submission: str, rubric: str, subject: str) -> Dict:
        """Grade assignment using AI - TEACHER TOOL"""
        system_message = f"You are an expert {subject} teacher grading assignments with fairness and consistency."
        
        prompt = f"""
        Grade this assignment based on the following rubric:
        
        RUBRIC:
        {rubric}
        
        STUDENT SUBMISSION:
        {submission}
        
        Provide:
        1. Overall grade (0-100)
        2. Detailed feedback explaining the grade
        3. Specific areas for improvement
        4. Strengths identified
        5. Suggestions for next steps
        
        Format as JSON:
        {{
            "grade": 85,
            "feedback": "Detailed feedback here",
            "improvements": ["Area 1", "Area 2"],
            "strengths": ["Strength 1", "Strength 2"],
            "next_steps": ["Suggestion 1", "Suggestion 2"]
        }}
        """
        
        response = await self.get_ai_response(prompt, system_message)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "grade": 0,
                "feedback": response,
                "improvements": [],
                "strengths": [],
                "next_steps": []
            }
    
    async def create_lesson_plan(self, subject: str, topic: str, grade_level: str, duration: str = "60 minutes") -> Dict:
        """Create lesson plan using AI - TEACHER TOOL"""
        system_message = f"You are an expert {subject} teacher creating comprehensive lesson plans."
        
        prompt = f"""
        Create a detailed lesson plan for {topic} in {subject} for {grade_level} students.
        Duration: {duration}
        
        Include:
        1. Learning objectives
        2. Materials needed
        3. Step-by-step lesson structure
        4. Assessment methods
        5. Differentiation strategies
        6. Time allocation for each activity
        7. Homework/extension activities
        
        Format as JSON with these sections.
        """
        
        response = await self.get_ai_response(prompt, system_message)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "topic": topic,
                "subject": subject,
                "grade_level": grade_level,
                "duration": duration,
                "raw_response": response
            }
    
    async def generate_practice_problems(self, subject: str, topic: str, difficulty: str, num_problems: int = 5) -> List[Dict]:
        """Generate practice problems using AI - TEACHER TOOL"""
        system_message = f"You are an expert {subject} teacher creating practice materials."
        
        prompt = f"""
        Create {num_problems} {difficulty} level practice problems about {topic} in {subject}.
        
        For each problem include:
        1. Problem statement
        2. Step-by-step solution
        3. Key concepts tested
        4. Tips for solving
        5. Common mistakes to avoid
        
        Format as JSON array of problem objects.
        """
        
        response = await self.get_ai_response(prompt, system_message)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return [{"problem": response, "solution": "", "concepts": [], "tips": []}]
    
    async def analyze_student_performance(self, student_data: Dict) -> Dict:
        """Analyze student performance and provide teacher insights - TEACHER TOOL"""
        system_message = "You are an educational psychologist providing insights to help teachers support their students."
        
        prompt = f"""
        Analyze this student's performance data and provide insights for the teacher:
        
        STUDENT DATA:
        {json.dumps(student_data, indent=2)}
        
        Provide:
        1. Performance summary
        2. Identified strengths
        3. Areas needing improvement
        4. Teaching strategies to support this student
        5. Intervention recommendations
        6. Progress monitoring suggestions
        
        Format as JSON with these fields.
        """
        
        response = await self.get_ai_response(prompt, system_message)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "summary": response,
                "strengths": [],
                "improvements": [],
                "teaching_strategies": [],
                "interventions": [],
                "monitoring": []
            }
    
    async def create_assessment_rubric(self, assignment_type: str, subject: str, grade_level: str) -> Dict:
        """Create assessment rubric using AI - TEACHER TOOL"""
        system_message = f"You are an expert {subject} teacher creating fair and comprehensive assessment rubrics."
        
        prompt = f"""
        Create a detailed assessment rubric for {assignment_type} in {subject} for {grade_level} students.
        
        Include:
        1. Clear criteria for each grade level (A, B, C, D, F)
        2. Specific descriptors for each criterion
        3. Point allocation
        4. Assessment standards
        5. Examples of what constitutes each grade level
        
        Format as JSON with these sections.
        """
        
        response = await self.get_ai_response(prompt, system_message)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "assignment_type": assignment_type,
                "subject": subject,
                "grade_level": grade_level,
                "raw_response": response
            }
    
    async def generate_educational_content(self, content_type: str, subject: str, topic: str, grade_level: str) -> str:
        """Generate educational content using AI - TEACHER TOOL"""
        system_message = f"You are an expert {subject} teacher creating {content_type} content for {grade_level} students."
        
        prompt = f"""
        Create {content_type} content about {topic} in {subject} for {grade_level} students.
        
        Requirements:
        - Clear and engaging
        - Educational and informative
        - Include examples where appropriate
        - Structured and well-organized
        - Suitable for {grade_level} level
        - Include key learning points
        - Provide discussion questions or activities
        
        Format the content appropriately for {content_type}.
        """
        
        return await self.get_ai_response(prompt, system_message)
    
    async def provide_teaching_feedback(self, lesson_description: str, student_responses: List[str], subject: str) -> Dict:
        """Provide feedback on teaching effectiveness - TEACHER TOOL"""
        system_message = f"You are an expert {subject} teacher providing constructive feedback on teaching methods."
        
        prompt = f"""
        Analyze this teaching scenario and provide feedback:
        
        Lesson Description: {lesson_description}
        Student Responses: {student_responses}
        Subject: {subject}
        
        Provide:
        1. Teaching effectiveness assessment
        2. What worked well
        3. Areas for improvement
        4. Alternative teaching strategies
        5. Student engagement suggestions
        6. Assessment of student understanding
        
        Format as JSON with these sections.
        """
        
        response = await self.get_ai_response(prompt, system_message)
        
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            return {
                "effectiveness": "Not determined",
                "strengths": [],
                "improvements": [],
                "strategies": [],
                "engagement": [],
                "understanding": "Not determined",
                "raw_response": response
            }

# Create global AI service instance for teachers only
teacher_ai = TeacherAI()
