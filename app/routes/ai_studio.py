from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
import os
from ..services.ai_service import ai_assistant
from ..core.auth import get_current_teacher
from pydantic import BaseModel
from typing import Dict

router = APIRouter()

class GenerativeRequest(BaseModel):
    topic: str
    scenario_type: str = "database"
    
@router.post("/synthesize-dataset")
def synthesize_dataset(req: GenerativeRequest, current_teacher = Depends(get_current_teacher)):
    """Generates unique scenario mock CSV data using AI."""
    return ai_assistant.synthesize_unique_dataset(req.scenario_type)

@router.post("/generate-study-plan")
def generate_study_plan(req: GenerativeRequest, current_teacher = Depends(get_current_teacher)):
    """Generates a study plan using AI."""
    return {"plan": ai_assistant.generate_study_plan(req.topic, 4)}

class AIGradeRequest(BaseModel):
    question_text: str
    student_answer: str
    max_points: float

@router.post("/grade-answer")
def grade_answer(req: AIGradeRequest, current_teacher = Depends(get_current_teacher)):
    """Uses mock AI to grade a student's rationale."""
    return ai_assistant.grade_text_answer(req.question_text, req.student_answer, req.max_points)

class QuizGenerationRequest(BaseModel):
    content: str
    
@router.post("/generate-quiz")
def generate_quiz(req: QuizGenerationRequest, current_teacher = Depends(get_current_teacher)):
    """Passes raw text study material to Gemini to parse into a structured editable quiz JSON."""
    return ai_assistant.generate_quiz_from_content(req.content)

@router.post("/generate-quiz-file")
async def generate_quiz_file(file: UploadFile = File(...), current_teacher = Depends(get_current_teacher)):
    """Uploads study material file to Gemini to parse into a structured editable quiz JSON."""
    temp_file_path = f"temp_{file.filename}"
    try:
        # Save file temporarily
        content = await file.read()
        with open(temp_file_path, "wb") as f:
            f.write(content)
            
        # Generate quiz from file
        result = ai_assistant.generate_quiz_from_file(temp_file_path)
        return result
    finally:
        # Clean up local temp file
        if os.path.exists(temp_file_path):
            os.remove(temp_file_path)
