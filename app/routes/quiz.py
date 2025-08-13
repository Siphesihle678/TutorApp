from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from ..core.database import get_db
from ..core.auth import get_current_teacher, get_current_user, get_current_student
from ..models.user import User
from ..models.quiz import Quiz, Question, QuizAttempt, QuizSubmission, QuestionType
from ..models.performance import PerformanceRecord
from ..schemas.quiz import (
    QuizCreate, QuizRead, QuizUpdate, 
    QuestionCreate, QuestionRead,
    QuizAttemptCreate, QuizSubmissionCreate,
    QuizResult, QuizAnalytics
)
from ..services.email_service import send_quiz_notification

router = APIRouter()

# ==================== QUIZ MANAGEMENT (TEACHERS) ====================

@router.post("/", response_model=QuizRead)
def create_quiz(
    quiz_data: QuizCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Create a new quiz with questions"""
    # Create quiz
    quiz = Quiz(
        title=quiz_data.title,
        description=quiz_data.description,
        subject=quiz_data.subject,
        time_limit=quiz_data.time_limit,
        passing_score=quiz_data.passing_score,
        creator_id=current_teacher.id
    )
    db.add(quiz)
    db.commit()
    db.refresh(quiz)
    
    # Add questions
    for question_data in quiz_data.questions:
        question = Question(
            text=question_data.text,
            question_type=question_data.question_type,
            options=question_data.options,
            correct_answer=question_data.correct_answer,
            points=question_data.points,
            explanation=question_data.explanation,
            quiz_id=quiz.id
        )
        db.add(question)
    
    db.commit()
    
    # Notify students about new quiz
    students = db.query(User).filter(User.role == "student", User.is_active == True).all()
    for student in students:
        send_quiz_notification(student.email, student.name, quiz.title, quiz.subject)
    
    return quiz

@router.get("/", response_model=List[QuizRead])
def get_quizzes(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    active_only: bool = True
):
    """Get all quizzes (filtered by user role)"""
    query = db.query(Quiz)
    
    if active_only:
        query = query.filter(Quiz.is_active == True)
    
    if current_user.role == "teacher":
        # Teachers see their own quizzes
        quizzes = query.filter(Quiz.creator_id == current_user.id).all()
    else:
        # Students see all active quizzes
        quizzes = query.all()
    
    return quizzes

@router.get("/{quiz_id}", response_model=QuizRead)
def get_quiz(
    quiz_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quiz details"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Check if user has access
    if current_user.role == "student" and not quiz.is_active:
        raise HTTPException(status_code=403, detail="Quiz not available")
    
    if current_user.role == "teacher" and quiz.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return quiz

@router.put("/{quiz_id}", response_model=QuizRead)
def update_quiz(
    quiz_id: int,
    quiz_data: QuizUpdate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Update quiz details"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.creator_id == current_teacher.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    for field, value in quiz_data.dict(exclude_unset=True).items():
        setattr(quiz, field, value)
    
    db.commit()
    db.refresh(quiz)
    return quiz

@router.delete("/{quiz_id}")
def delete_quiz(
    quiz_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Delete a quiz"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.creator_id == current_teacher.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    db.delete(quiz)
    db.commit()
    return {"message": "Quiz deleted successfully"}

@router.post("/{quiz_id}/toggle")
def toggle_quiz_status(
    quiz_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Toggle quiz active status"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.creator_id == current_teacher.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    quiz.is_active = not quiz.is_active
    db.commit()
    
    status = "activated" if quiz.is_active else "deactivated"
    return {"message": f"Quiz {status} successfully"}

# ==================== QUIZ TAKING (STUDENTS) ====================

@router.post("/{quiz_id}/start")
def start_quiz(
    quiz_id: int,
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Start a quiz attempt"""
    # Check if quiz exists and is active
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.is_active == True).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found or not active")
    
    # Check if student already has an active attempt
    existing_attempt = db.query(QuizAttempt).filter(
        QuizAttempt.quiz_id == quiz_id,
        QuizAttempt.student_id == current_student.id,
        QuizAttempt.completed_at == None
    ).first()
    
    if existing_attempt:
        # Return existing attempt
        return {
            "attempt_id": existing_attempt.id,
            "started_at": existing_attempt.started_at,
            "message": "Resuming existing quiz attempt"
        }
    
    # Create new attempt
    attempt = QuizAttempt(
        quiz_id=quiz_id,
        student_id=current_student.id,
        started_at=datetime.utcnow()
    )
    db.add(attempt)
    db.commit()
    db.refresh(attempt)
    
    return {
        "attempt_id": attempt.id,
        "started_at": attempt.started_at,
        "message": "Quiz attempt started successfully"
    }

@router.post("/{quiz_id}/submit")
def submit_quiz(
    quiz_id: int,
    submissions: List[QuizSubmissionCreate],
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Submit quiz answers and get results"""
    try:
        # Get active attempt
        attempt = db.query(QuizAttempt).filter(
            QuizAttempt.quiz_id == quiz_id,
            QuizAttempt.student_id == current_student.id,
            QuizAttempt.completed_at == None
        ).first()
        
        if not attempt:
            raise HTTPException(status_code=404, detail="No active quiz attempt found")
        
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")
        
        total_score = 0
        total_points = 0
        
        # Process each submission
        for submission_data in submissions:
            question = db.query(Question).filter(Question.id == submission_data.question_id).first()
            if not question:
                continue
            
            # Check if answer is correct
            is_correct = False
            points_earned = 0
            
            if question.question_type == QuestionType.MULTIPLE_CHOICE:
                is_correct = submission_data.answer.lower().strip() == question.correct_answer.lower().strip()
            elif question.question_type == QuestionType.TRUE_FALSE:
                is_correct = submission_data.answer.lower().strip() == question.correct_answer.lower().strip()
            elif question.question_type == QuestionType.SHORT_ANSWER:
                # For short answer, check for partial matches
                student_answer = submission_data.answer.lower().strip()
                correct_answer = question.correct_answer.lower().strip()
                is_correct = student_answer == correct_answer
            
            if is_correct:
                points_earned = question.points
            
            # Create submission record
            submission = QuizSubmission(
                question_id=submission_data.question_id,
                attempt_id=attempt.id,
                answer=submission_data.answer,
                is_correct=is_correct,
                points_earned=points_earned
            )
            db.add(submission)
            
            total_score += points_earned
            total_points += question.points
        
        # Calculate final score and percentage
        percentage = (total_score / total_points * 100) if total_points > 0 else 0
        is_passed = percentage >= quiz.passing_score
        
        # Update attempt
        attempt.completed_at = datetime.utcnow()
        attempt.score = total_score
        attempt.is_passed = is_passed
        attempt.time_taken = int((attempt.completed_at - attempt.started_at).total_seconds())
        
        # Commit the changes
        db.commit()
        
        return {
            "score": total_score,
            "max_score": total_points,
            "percentage": round(percentage, 2),
            "is_passed": is_passed,
            "time_taken": attempt.time_taken
        }
        
    except HTTPException:
        # Re-raise HTTP exceptions as they are already properly formatted
        raise
    except Exception as e:
        # Log the error for debugging
        print(f"Error in quiz submission: {str(e)}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        # Rollback any database changes
        db.rollback()
        # Return a proper JSON error response
        raise HTTPException(
            status_code=500, 
            detail="An error occurred while processing your quiz submission. Please try again."
        )

# ==================== QUIZ ANALYTICS ====================

@router.get("/{quiz_id}/analytics", response_model=QuizAnalytics)
def get_quiz_analytics(
    quiz_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for a quiz"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.creator_id == current_teacher.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    # Get all attempts for this quiz
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    
    if not attempts:
        return {
            "quiz_id": quiz_id,
            "total_attempts": 0,
            "average_score": 0,
            "pass_rate": 0,
            "average_time": 0,
            "question_analytics": []
        }
    
    # Calculate statistics
    total_attempts = len(attempts)
    completed_attempts = [a for a in attempts if a.completed_at]
    passed_attempts = [a for a in completed_attempts if a.is_passed]
    
    average_score = sum(a.score for a in completed_attempts) / len(completed_attempts) if completed_attempts else 0
    pass_rate = (len(passed_attempts) / len(completed_attempts) * 100) if completed_attempts else 0
    average_time = sum(a.time_taken for a in completed_attempts) / len(completed_attempts) if completed_attempts else 0
    
    # Question-level analytics
    question_analytics = []
    for question in quiz.questions:
        submissions = db.query(QuizSubmission).join(QuizAttempt).filter(
            QuizSubmission.question_id == question.id,
            QuizAttempt.quiz_id == quiz_id
        ).all()
        
        if submissions:
            correct_count = sum(1 for s in submissions if s.is_correct)
            success_rate = (correct_count / len(submissions) * 100)
        else:
            success_rate = 0
        
        question_analytics.append({
            "question_id": question.id,
            "question_text": question.text,
            "success_rate": round(success_rate, 2),
            "total_attempts": len(submissions)
        })
    
    return {
        "quiz_id": quiz_id,
        "total_attempts": total_attempts,
        "average_score": round(average_score, 2),
        "pass_rate": round(pass_rate, 2),
        "average_time": round(average_time, 2),
        "question_analytics": question_analytics
    }

@router.get("/{quiz_id}/attempts")
def get_quiz_attempts(
    quiz_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get all attempts for a quiz"""
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id, Quiz.creator_id == current_teacher.id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    
    attempts = db.query(QuizAttempt).filter(QuizAttempt.quiz_id == quiz_id).all()
    
    return [
        {
            "id": attempt.id,
            "student_name": attempt.student.name,
            "student_email": attempt.student.email,
            "started_at": attempt.started_at,
            "completed_at": attempt.completed_at,
            "score": attempt.score,
            "is_passed": attempt.is_passed,
            "time_taken": attempt.time_taken
        }
        for attempt in attempts
    ]
