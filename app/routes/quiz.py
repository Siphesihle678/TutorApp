from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..core.database import get_db
from ..core.auth import get_current_teacher, get_current_student, get_current_user
from ..models.user import User
from ..models.quiz import Quiz, Question, QuizAttempt, QuizSubmission
from ..models.performance import PerformanceRecord
from ..schemas.quiz import (
    QuizCreate, QuizRead, QuizAttemptCreate, QuizAttemptRead,
    QuizSubmissionCreate, QuizResult
)
from ..services.email_service import email_service

router = APIRouter()

@router.post("/", response_model=QuizRead)
def create_quiz(
    quiz_data: QuizCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Create a new quiz (teachers only)"""
    # Create quiz
    db_quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        subject=quiz_data.subject,
        time_limit=quiz_data.time_limit,
        passing_score=quiz_data.passing_score,
        creator_id=current_teacher.id
    )
    db.add(db_quiz)
    db.commit()
    db.refresh(db_quiz)
    
    # Create questions
    for question_data in quiz_data.questions:
        db_question = Question(
            text=question_data.text,
            question_type=question_data.question_type,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            points=question_data.points,
            explanation=question_data.explanation,
            quiz_id=db_quiz.id
        )
        db.add(db_question)
    
    db.commit()
    db.refresh(db_quiz)
    return db_quiz

@router.get("/", response_model=List[QuizRead])
def list_quizzes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all active quizzes"""
    quizzes = db.query(Quiz).filter(Quiz.is_active == True).all()
    return quizzes

@router.get("/{quiz_id}", response_model=QuizRead)
def get_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quiz details"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_active == True).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return quiz

@router.post("/{quiz_id}/start", response_model=QuizAttemptRead)
def start_quiz(
    quiz_id: int,
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Start a quiz attempt"""
    # Check if quiz exists and is active
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_active == True).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Check if student already has an active attempt
    existing_attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == current_student.id,
        QuizAttempt.completed_at == None
    ).first()
    
    if existing_attempt:
        raise HTTPException(status_code=400, detail="You already have an active attempt for this quiz")
    
    # Create new attempt
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_id=current_student.id
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return attempt

@router.post("/{quiz_id}/submit", response_model=QuizResult)
def submit_quiz(
    quiz_id: int,
    submissions: List[QuizSubmissionCreate],
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Submit quiz answers and get results"""
    # Get active attempt
    attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == current_student.id,
        QuizAttempt.completed_at == None
    ).first()
    
    if not attempt:
        raise HTTPException(status_code=400, detail="No active attempt found")
    
    # Get quiz and questions
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    questions = db.query(Question).filter(Question.quiz_id == quiz_id).all()
    
    # Process submissions
    total_score = 0
    max_score = sum(q.points for q in questions)
    question_results = []
    
    for submission_data in submissions:
        question = next((q for q in questions if q.id == submission_data.question_id), None)
        if not question:
            continue
        
        # Check if answer is correct
        is_correct = submission_data.answer.lower().strip() == question.correct_answer.lower().strip()
        points_earned = question.points if is_correct else 0
        total_score += points_earned
        
        # Save submission
        submission = QuizSubmission(
            question_id=question.id,
            attempt_id=attempt.id,
            answer=submission_data.answer,
            is_correct=is_correct,
            points_earned=points_earned
        )
        db.add(submission)
        
        question_results.append({
            "question_id": question.id,
            "question_text": question.text,
            "student_answer": submission_data.answer,
            "correct_answer": question.correct_answer,
            "is_correct": is_correct,
            "points_earned": points_earned,
            "max_points": question.points,
            "explanation": question.explanation
        })
    
    # Calculate percentage and determine if passed
    percentage = (total_score / max_score) * 100 if max_score > 0 else 0
    is_passed = percentage >= quiz.passing_score
    
    # Update attempt
    attempt.completed_at = datetime.utcnow()
    attempt.score = total_score
    attempt.is_passed = is_passed
    attempt.time_taken = int((attempt.completed_at - attempt.started_at).total_seconds())
    
    # Create performance record
    performance_record = PerformanceRecord(
        student_id=current_student.id,
        subject=quiz.subject,
        assessment_type="quiz",
        assessment_id=quiz.id,
        score=total_score,
        max_score=max_score,
        percentage=percentage,
        time_taken=attempt.time_taken,
        strengths=[],  # TODO: Analyze strengths based on correct answers
        weaknesses=[],  # TODO: Analyze weaknesses based on incorrect answers
        recommendations=f"Keep practicing {quiz.subject} concepts to improve your understanding."
    )
    db.add(performance_record)
    
    db.commit()
    
    return QuizResult(
        attempt_id=attempt.id,
        score=total_score,
        max_score=max_score,
        percentage=percentage,
        is_passed=is_passed,
        time_taken=attempt.time_taken,
        question_results=question_results
    )

@router.get("/{quiz_id}/attempts", response_model=List[QuizAttemptRead])
def get_quiz_attempts(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quiz attempts (teachers can see all, students see only their own)"""
    if current_user.role == "teacher":
        attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    else:
        attempts = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.student_id == current_user.id
        ).all()
    
    return attempts
