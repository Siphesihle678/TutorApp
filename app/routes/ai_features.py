from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from ..core.database import get_db
from ..core.auth import get_current_teacher
from ..models.user import User
from ..services.ai_service import teacher_ai
from ..schemas.ai_features import (
    QuizGenerationRequest, QuizGenerationResponse,
    AssignmentGradingRequest, AssignmentGradingResponse,
    LessonPlanRequest, LessonPlanResponse,
    PracticeProblemsRequest, PracticeProblemsResponse,
    PerformanceAnalysisRequest, PerformanceAnalysisResponse,
    RubricCreationRequest, RubricCreationResponse,
    ContentGenerationRequest, ContentGenerationResponse,
    TeachingFeedbackRequest, TeachingFeedbackResponse
)

router = APIRouter()

@router.post("/generate-quiz", response_model=QuizGenerationResponse)
async def generate_quiz_ai(
    request: QuizGenerationRequest,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Generate quiz questions using AI - TEACHER ONLY"""
    try:
        quiz_data = await teacher_ai.generate_quiz(
            subject=request.subject,
            topic=request.topic,
            difficulty=request.difficulty,
            num_questions=request.num_questions
        )
        
        return QuizGenerationResponse(
            success=True,
            quiz_data=quiz_data,
            message="Quiz generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/grade-assignment", response_model=AssignmentGradingResponse)
async def grade_assignment_ai(
    request: AssignmentGradingRequest,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Grade assignment using AI - TEACHER ONLY"""
    try:
        grading_result = await teacher_ai.grade_assignment(
            submission=request.submission,
            rubric=request.rubric,
            subject=request.subject
        )
        
        return AssignmentGradingResponse(
            success=True,
            grade=grading_result.get("grade", 0),
            feedback=grading_result.get("feedback", ""),
            improvements=grading_result.get("improvements", []),
            strengths=grading_result.get("strengths", []),
            next_steps=grading_result.get("next_steps", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/create-lesson-plan", response_model=LessonPlanResponse)
async def create_lesson_plan_ai(
    request: LessonPlanRequest,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Create lesson plan using AI - TEACHER ONLY"""
    try:
        lesson_plan = await teacher_ai.create_lesson_plan(
            subject=request.subject,
            topic=request.topic,
            grade_level=request.grade_level,
            duration=request.duration
        )
        
        return LessonPlanResponse(
            success=True,
            lesson_plan=lesson_plan,
            message="Lesson plan created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/generate-practice-problems", response_model=PracticeProblemsResponse)
async def generate_practice_problems_ai(
    request: PracticeProblemsRequest,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Generate practice problems using AI - TEACHER ONLY"""
    try:
        problems = await teacher_ai.generate_practice_problems(
            subject=request.subject,
            topic=request.topic,
            difficulty=request.difficulty,
            num_problems=request.num_problems
        )
        
        return PracticeProblemsResponse(
            success=True,
            problems=problems,
            message="Practice problems generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/analyze-performance", response_model=PerformanceAnalysisResponse)
async def analyze_student_performance_ai(
    request: PerformanceAnalysisRequest,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Analyze student performance using AI - TEACHER ONLY"""
    try:
        analysis = await teacher_ai.analyze_student_performance(
            student_data=request.student_data
        )
        
        return PerformanceAnalysisResponse(
            success=True,
            summary=analysis.get("summary", ""),
            strengths=analysis.get("strengths", []),
            improvements=analysis.get("improvements", []),
            teaching_strategies=analysis.get("teaching_strategies", []),
            interventions=analysis.get("interventions", []),
            monitoring=analysis.get("monitoring", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/create-rubric", response_model=RubricCreationResponse)
async def create_assessment_rubric_ai(
    request: RubricCreationRequest,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Create assessment rubric using AI - TEACHER ONLY"""
    try:
        rubric = await teacher_ai.create_assessment_rubric(
            assignment_type=request.assignment_type,
            subject=request.subject,
            grade_level=request.grade_level
        )
        
        return RubricCreationResponse(
            success=True,
            rubric=rubric,
            message="Assessment rubric created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/generate-content", response_model=ContentGenerationResponse)
async def generate_educational_content_ai(
    request: ContentGenerationRequest,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Generate educational content using AI - TEACHER ONLY"""
    try:
        content = await teacher_ai.generate_educational_content(
            content_type=request.content_type,
            subject=request.subject,
            topic=request.topic,
            grade_level=request.grade_level
        )
        
        return ContentGenerationResponse(
            success=True,
            content=content,
            message="Educational content generated successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")

@router.post("/teaching-feedback", response_model=TeachingFeedbackResponse)
async def provide_teaching_feedback_ai(
    request: TeachingFeedbackRequest,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Provide feedback on teaching effectiveness - TEACHER ONLY"""
    try:
        feedback = await teacher_ai.provide_teaching_feedback(
            lesson_description=request.lesson_description,
            student_responses=request.student_responses,
            subject=request.subject
        )
        
        return TeachingFeedbackResponse(
            success=True,
            effectiveness=feedback.get("effectiveness", ""),
            strengths=feedback.get("strengths", []),
            improvements=feedback.get("improvements", []),
            strategies=feedback.get("strategies", []),
            engagement=feedback.get("engagement", []),
            understanding=feedback.get("understanding", "")
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI service error: {str(e)}")
