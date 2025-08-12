from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
from ..core.database import get_db
from ..core.auth import get_current_teacher, get_current_student, get_current_user
from ..models.user import User
from ..models.assignment import Assignment, AssignmentSubmission
from ..models.performance import PerformanceRecord
from ..schemas.assignment import (
    AssignmentCreate, AssignmentRead, AssignmentSubmissionCreate,
    AssignmentSubmissionRead, AssignmentGrade
)
from ..services.email_service import email_service

router = APIRouter()

@router.post("/", response_model=AssignmentRead)
def create_assignment(
    assignment_data: AssignmentCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Create a new assignment (teachers only)"""
    db_assignment = Assignment(
        title=assignment_data.title,
        description=assignment_data.description,
        subject=assignment_data.subject,
        due_date=assignment_data.due_date,
        max_points=assignment_data.max_points,
        creator_id=current_teacher.id
    )
    
    db.add(db_assignment)
    db.commit()
    db.refresh(db_assignment)
    
    return db_assignment

@router.get("/", response_model=List[AssignmentRead])
def list_assignments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all active assignments"""
    assignments = db.query(Assignment).filter(Assignment.is_active == True).all()
    return assignments

@router.get("/{assignment_id}", response_model=AssignmentRead)
def get_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assignment details"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.is_active == True
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return assignment

@router.post("/{assignment_id}/submit", response_model=AssignmentSubmissionRead)
def submit_assignment(
    assignment_id: int,
    submission_data: AssignmentSubmissionCreate,
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Submit an assignment (students only)"""
    # Check if assignment exists and is active
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id,
        Assignment.is_active == True
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if student already submitted
    existing_submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == current_student.id
    ).first()
    
    if existing_submission:
        raise HTTPException(status_code=400, detail="You have already submitted this assignment")
    
    # Check if submission is late
    is_late = datetime.utcnow() > assignment.due_date
    
    # Create submission
    submission = AssignmentSubmission(
        assignment_id=assignment_id,
        student_id=current_student.id,
        content=submission_data.content,
        file_url=submission_data.file_url,
        is_late=is_late
    )
    
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    return submission

@router.get("/{assignment_id}/submissions", response_model=List[AssignmentSubmissionRead])
def get_assignment_submissions(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assignment submissions (teachers see all, students see only their own)"""
    if current_user.role == "teacher":
        submissions = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == assignment_id
        ).all()
    else:
        submissions = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == assignment_id,
            AssignmentSubmission.student_id == current_user.id
        ).all()
    
    return submissions

@router.post("/submissions/{submission_id}/grade")
def grade_assignment(
    submission_id: int,
    grade_data: AssignmentGrade,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Grade an assignment submission (teachers only)"""
    submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.id == submission_id
    ).first()
    
    if not submission:
        raise HTTPException(status_code=404, detail="Submission not found")
    
    # Update submission with grade
    submission.score = grade_data.score
    submission.feedback = grade_data.feedback
    submission.graded_at = datetime.utcnow()
    
    # Calculate percentage
    assignment = db.query(Assignment).filter(Assignment.id == submission.assignment_id).first()
    percentage = (grade_data.score / assignment.max_points) * 100 if assignment.max_points > 0 else 0
    
    # Create performance record
    performance_record = PerformanceRecord(
        student_id=submission.student_id,
        subject=assignment.subject,
        assessment_type="assignment",
        assessment_id=assignment.id,
        score=grade_data.score,
        max_score=assignment.max_points,
        percentage=percentage,
        strengths=[],  # TODO: Analyze strengths based on feedback
        weaknesses=[],  # TODO: Analyze weaknesses based on feedback
        recommendations=grade_data.feedback or f"Keep working on {assignment.subject} concepts."
    )
    db.add(performance_record)
    
    db.commit()
    
    # Send email notification to student
    student = db.query(User).filter(User.id == submission.student_id).first()
    if student:
        email_service.send_grade_notification(
            student.email,
            student.name,
            assignment.title,
            grade_data.score,
            assignment.max_points
        )
    
    return {"message": "Assignment graded successfully"}
