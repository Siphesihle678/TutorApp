from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from ..core.database import get_db
from ..core.auth import get_current_teacher, get_current_user, get_current_student
from ..models.user import User
from ..models.assignment import Assignment, AssignmentSubmission
from ..models.performance import PerformanceRecord
from ..schemas.assignment import (
    AssignmentCreate, AssignmentRead, AssignmentUpdate,
    AssignmentSubmissionCreate, AssignmentSubmissionRead,
    AssignmentGrade, AssignmentAnalytics
)
from ..services.email_service import send_assignment_notification, send_grade_notification

router = APIRouter()

# ==================== ASSIGNMENT MANAGEMENT (TEACHERS) ====================

@router.post("/", response_model=AssignmentRead)
def create_assignment(
    assignment_data: AssignmentCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Create a new assignment"""
    assignment = Assignment(
        title=assignment_data.title,
        description=assignment_data.description,
        subject=assignment_data.subject,
        max_points=assignment_data.max_points,
        due_date=assignment_data.due_date,
        creator_id=current_teacher.id
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    # Notify students about new assignment
    students = db.query(User).filter(User.role == "student", User.is_active == True).all()
    for student in students:
        send_assignment_notification(
            student.email, 
            student.name, 
            assignment.title, 
            assignment.subject,
            assignment.due_date
        )
    
    return assignment

@router.get("/", response_model=List[AssignmentRead])
def get_assignments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    active_only: bool = True
):
    """Get all assignments (filtered by user role)"""
    query = db.query(Assignment)
    
    if active_only:
        query = query.filter(Assignment.is_active == True)
    
    if current_user.role == "teacher":
        # Teachers see their own assignments
        assignments = query.filter(Assignment.creator_id == current_user.id).all()
    else:
        # Students see all active assignments
        assignments = query.all()
    
    return assignments

@router.get("/{assignment_id}", response_model=AssignmentRead)
def get_assignment(
    assignment_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get assignment details"""
    assignment = db.query(Assignment).filter(Assignment.id == assignment_id).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if user has access
    if current_user.role == "student" and not assignment.is_active:
        raise HTTPException(status_code=403, detail="Assignment not available")
    
    if current_user.role == "teacher" and assignment.creator_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return assignment

@router.put("/{assignment_id}", response_model=AssignmentRead)
def update_assignment(
    assignment_id: int,
    assignment_data: AssignmentUpdate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Update assignment details"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id, 
        Assignment.creator_id == current_teacher.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    for field, value in assignment_data.dict(exclude_unset=True).items():
        setattr(assignment, field, value)
    
    db.commit()
    db.refresh(assignment)
    return assignment

@router.delete("/{assignment_id}")
def delete_assignment(
    assignment_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Delete an assignment"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id, 
        Assignment.creator_id == current_teacher.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    db.delete(assignment)
    db.commit()
    return {"message": "Assignment deleted successfully"}

@router.post("/{assignment_id}/toggle")
def toggle_assignment_status(
    assignment_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Toggle assignment active status"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id, 
        Assignment.creator_id == current_teacher.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    assignment.is_active = not assignment.is_active
    db.commit()
    
    status = "activated" if assignment.is_active else "deactivated"
    return {"message": f"Assignment {status} successfully"}

# ==================== ASSIGNMENT SUBMISSION (STUDENTS) ====================

@router.post("/{assignment_id}/submit", response_model=AssignmentSubmissionRead)
def submit_assignment(
    assignment_id: int,
    submission_data: AssignmentSubmissionCreate,
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Submit an assignment"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id, 
        Assignment.is_active == True
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if assignment is still open
    if assignment.due_date and datetime.utcnow() > assignment.due_date:
        raise HTTPException(status_code=400, detail="Assignment deadline has passed")
    
    # Check if student already submitted
    existing_submission = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id,
        AssignmentSubmission.student_id == current_student.id
    ).first()
    
    if existing_submission:
        raise HTTPException(status_code=400, detail="You have already submitted this assignment")
    
    # Create submission
    submission = AssignmentSubmission(
        assignment_id=assignment_id,
        student_id=current_student.id,
        content=submission_data.content,
        submitted_at=datetime.utcnow()
    )
    db.add(submission)
    db.commit()
    db.refresh(submission)
    
    return submission

@router.get("/{assignment_id}/submissions", response_model=List[AssignmentSubmissionRead])
def get_assignment_submissions(
    assignment_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get all submissions for an assignment (teachers only)"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id, 
        Assignment.creator_id == current_teacher.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id
    ).all()
    
    return submissions

@router.get("/submissions/my", response_model=List[AssignmentSubmissionRead])
def get_my_submissions(
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get student's own submissions"""
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.student_id == current_student.id
    ).all()
    
    return submissions

# ==================== ASSIGNMENT GRADING (TEACHERS) ====================

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
    
    # Verify teacher owns the assignment
    assignment = db.query(Assignment).filter(
        Assignment.id == submission.assignment_id,
        Assignment.creator_id == current_teacher.id
    ).first()
    
    if not assignment:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Update submission with grade
    submission.score = grade_data.grade
    submission.feedback = grade_data.feedback
    submission.graded_at = datetime.utcnow()
    submission.graded_by = current_teacher.id
    
    # Calculate percentage
    percentage = (grade_data.grade / assignment.max_points) * 100 if assignment.max_points > 0 else 0
    
    # Create performance record
    performance_record = PerformanceRecord(
        student_id=submission.student_id,
        subject=assignment.subject,
        assessment_type="assignment",
        assessment_id=assignment.id,
        score=grade_data.grade,
        max_score=assignment.max_points,
        percentage=percentage,
        strengths=[],
        weaknesses=[],
        recommendations=grade_data.feedback or f"Keep working on {assignment.subject} concepts."
    )
    db.add(performance_record)
    
    db.commit()
    
    # Send email notification to student
    student = db.query(User).filter(User.id == submission.student_id).first()
    if student:
        send_grade_notification(
            student.email,
            student.name,
            assignment.title,
            grade_data.grade,
            assignment.max_points
        )
    
    return {"message": "Assignment graded successfully"}

# ==================== ASSIGNMENT ANALYTICS ====================

@router.get("/{assignment_id}/analytics", response_model=AssignmentAnalytics)
def get_assignment_analytics(
    assignment_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get detailed analytics for an assignment"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id, 
        Assignment.creator_id == current_teacher.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Get all submissions for this assignment
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id
    ).all()
    
    if not submissions:
        return {
            "assignment_id": assignment_id,
            "total_submissions": 0,
            "submitted_count": 0,
            "graded_count": 0,
            "average_score": 0,
            "submission_rate": 0,
            "late_submissions": 0
        }
    
    # Calculate statistics
    total_students = db.query(User).filter(User.role == "student", User.is_active == True).count()
    submitted_count = len(submissions)
    graded_submissions = [s for s in submissions if s.score is not None]
    late_submissions = [s for s in submissions if assignment.due_date and s.submitted_at > assignment.due_date]
    
    average_score = sum(s.score for s in graded_submissions) / len(graded_submissions) if graded_submissions else 0
    submission_rate = (submitted_count / total_students * 100) if total_students > 0 else 0
    
    return {
        "assignment_id": assignment_id,
        "total_submissions": submitted_count,
        "submitted_count": submitted_count,
        "graded_count": len(graded_submissions),
        "average_score": round(average_score, 2),
        "submission_rate": round(submission_rate, 2),
        "late_submissions": len(late_submissions)
    }

# ==================== ASSIGNMENT DASHBOARD ====================

@router.get("/dashboard/overview")
def get_assignment_overview(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get assignment overview for teacher dashboard"""
    # Count assignments
    total_assignments = db.query(Assignment).filter(
        Assignment.creator_id == current_teacher.id
    ).count()
    
    active_assignments = db.query(Assignment).filter(
        Assignment.creator_id == current_teacher.id,
        Assignment.is_active == True
    ).count()
    
    # Count submissions
    total_submissions = db.query(AssignmentSubmission).join(Assignment).filter(
        Assignment.creator_id == current_teacher.id
    ).count()
    
    # Count pending grades
    pending_grades = db.query(AssignmentSubmission).join(Assignment).filter(
        Assignment.creator_id == current_teacher.id,
        AssignmentSubmission.score == None
    ).count()
    
    # Recent assignments
    recent_assignments = db.query(Assignment).filter(
        Assignment.creator_id == current_teacher.id
    ).order_by(desc(Assignment.created_at)).limit(5).all()
    
    return {
        "total_assignments": total_assignments,
        "active_assignments": active_assignments,
        "total_submissions": total_submissions,
        "pending_grades": pending_grades,
        "recent_assignments": [
            {
                "id": a.id,
                "title": a.title,
                "subject": a.subject,
                "due_date": a.due_date,
                "submission_count": db.query(AssignmentSubmission).filter(
                    AssignmentSubmission.assignment_id == a.id
                ).count()
            }
            for a in recent_assignments
        ]
    }

# ==================== ASSIGNMENT EXPORT ====================

@router.get("/{assignment_id}/export")
def export_assignment_data(
    assignment_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Export assignment data for analysis"""
    assignment = db.query(Assignment).filter(
        Assignment.id == assignment_id, 
        Assignment.creator_id == current_teacher.id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    submissions = db.query(AssignmentSubmission).filter(
        AssignmentSubmission.assignment_id == assignment_id
    ).all()
    
    return {
        "assignment": {
            "id": assignment.id,
            "title": assignment.title,
            "subject": assignment.subject,
            "max_points": assignment.max_points,
            "due_date": assignment.due_date,
            "created_at": assignment.created_at
        },
        "submissions": [
            {
                "id": s.id,
                "student_name": s.student.name,
                "student_email": s.student.email,
                "content": s.content,
                "submitted_at": s.submitted_at,
                "score": s.score,
                "feedback": s.feedback,
                "is_late": assignment.due_date and s.submitted_at > assignment.due_date
            }
            for s in submissions
        ],
        "statistics": {
            "total_submissions": len(submissions),
            "graded_submissions": len([s for s in submissions if s.score is not None]),
            "average_score": sum(s.score for s in submissions if s.score) / len([s for s in submissions if s.score]) if any(s.score for s in submissions) else 0,
            "late_submissions": len([s for s in submissions if assignment.due_date and s.submitted_at > assignment.due_date])
        }
    }
