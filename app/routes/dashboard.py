from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List
from ..core.database import get_db
from ..core.auth import get_current_teacher, get_current_user
from ..models.user import User
from ..models.quiz import Quiz, QuizAttempt
from ..models.assignment import Assignment, AssignmentSubmission
from ..models.performance import PerformanceRecord
from ..schemas.performance import StudentPerformance, LeaderboardEntry, DiagnosticReport

router = APIRouter()

@router.get("/teacher/overview")
def get_teacher_overview(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get teacher dashboard overview"""
    # Count students
    total_students = db.query(User).filter(User.role == "student", User.is_active == True).count()
    
    # Count active quizzes and assignments
    total_quizzes = db.query(Quiz).filter(Quiz.is_active == True).count()
    total_assignments = db.query(Assignment).filter(Assignment.is_active == True).count()
    
    # Count recent submissions
    recent_quiz_attempts = db.query(QuizAttempt).filter(
        QuizAttempt.completed_at != None
    ).count()
    
    recent_assignment_submissions = db.query(AssignmentSubmission).count()
    
    # Average performance
    avg_performance = db.query(func.avg(PerformanceRecord.percentage)).scalar() or 0
    
    return {
        "total_students": total_students,
        "total_quizzes": total_quizzes,
        "total_assignments": total_assignments,
        "recent_quiz_attempts": recent_quiz_attempts,
        "recent_assignment_submissions": recent_assignment_submissions,
        "average_performance": round(avg_performance, 2)
    }

@router.get("/teacher/students", response_model=List[StudentPerformance])
def get_student_performances(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get all students' performance data"""
    students = db.query(User).filter(User.role == "student", User.is_active == True).all()
    performances = []
    
    for student in students:
        # Get quiz attempts
        quiz_attempts = db.query(QuizAttempt).filter(
            QuizAttempt.student_id == student.id,
            QuizAttempt.completed_at != None
        ).all()
        
        # Get assignment submissions
        assignment_submissions = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.student_id == student.id
        ).all()
        
        # Calculate averages
        total_quiz_score = sum(attempt.score for attempt in quiz_attempts if attempt.score)
        total_assignment_score = sum(sub.score for sub in assignment_submissions if sub.score)
        
        avg_quiz_score = total_quiz_score / len(quiz_attempts) if quiz_attempts else 0
        avg_assignment_score = total_assignment_score / len(assignment_submissions) if assignment_submissions else 0
        
        # Calculate overall percentage
        total_assessments = len(quiz_attempts) + len(assignment_submissions)
        if total_assessments > 0:
            overall_percentage = ((total_quiz_score + total_assignment_score) / 
                                (sum(attempt.quiz.passing_score * 100 for attempt in quiz_attempts) + 
                                 sum(sub.assignment.max_points for sub in assignment_submissions))) * 100
        else:
            overall_percentage = 0
        
        performance = StudentPerformance(
            student_id=student.id,
            student_name=student.name,
            total_quizzes=len(quiz_attempts),
            total_assignments=len(assignment_submissions),
            average_quiz_score=round(avg_quiz_score, 2),
            average_assignment_score=round(avg_assignment_score, 2),
            overall_percentage=round(overall_percentage, 2)
        )
        performances.append(performance)
    
    # Sort by overall percentage
    performances.sort(key=lambda x: x.overall_percentage, reverse=True)
    
    # Add rankings
    for i, performance in enumerate(performances):
        performance.rank = i + 1
    
    return performances

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get student leaderboard"""
    # Get all performance records
    performances = db.query(
        PerformanceRecord.student_id,
        func.sum(PerformanceRecord.score).label('total_score'),
        func.count(PerformanceRecord.id).label('total_assessments'),
        func.avg(PerformanceRecord.percentage).label('average_percentage')
    ).group_by(PerformanceRecord.student_id).order_by(
        desc('average_percentage')
    ).all()
    
    leaderboard = []
    for i, perf in enumerate(performances):
        student = db.query(User).filter(User.id == perf.student_id).first()
        if student:
            entry = LeaderboardEntry(
                rank=i + 1,
                student_id=student.id,
                student_name=student.name,
                total_score=perf.total_score,
                total_assessments=perf.total_assessments,
                average_percentage=round(perf.average_percentage, 2)
            )
            leaderboard.append(entry)
    
    return leaderboard

@router.get("/student/{student_id}/diagnostic", response_model=DiagnosticReport)
def get_student_diagnostic(
    student_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get detailed diagnostic report for a student"""
    student = db.query(User).filter(User.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Get performance records
    performance_records = db.query(PerformanceRecord).filter(
        PerformanceRecord.student_id == student_id
    ).order_by(PerformanceRecord.created_at.desc()).all()
    
    if not performance_records:
        raise HTTPException(status_code=404, detail="No performance data found for this student")
    
    # Calculate overall percentage
    overall_percentage = sum(record.percentage for record in performance_records) / len(performance_records)
    
    # Analyze strengths and weaknesses (simplified analysis)
    strengths = []
    weaknesses = []
    
    # Group by subject
    subjects = {}
    for record in performance_records:
        if record.subject not in subjects:
            subjects[record.subject] = []
        subjects[record.subject].append(record.percentage)
    
    for subject, percentages in subjects.items():
        avg_percentage = sum(percentages) / len(percentages)
        if avg_percentage >= 80:
            strengths.append(f"Strong performance in {subject}")
        elif avg_percentage < 60:
            weaknesses.append(f"Needs improvement in {subject}")
    
    # Determine improvement trend
    if len(performance_records) >= 2:
        recent_avg = sum(record.percentage for record in performance_records[:3]) / min(3, len(performance_records))
        older_avg = sum(record.percentage for record in performance_records[-3:]) / min(3, len(performance_records))
        
        if recent_avg > older_avg + 5:
            improvement_trend = "improving"
        elif recent_avg < older_avg - 5:
            improvement_trend = "declining"
        else:
            improvement_trend = "stable"
    else:
        improvement_trend = "insufficient_data"
    
    # Generate recommendations
    recommendations = []
    if weaknesses:
        recommendations.append("Focus on improving weak areas through additional practice")
    if overall_percentage < 70:
        recommendations.append("Consider seeking additional help or tutoring")
    if improvement_trend == "declining":
        recommendations.append("Review study habits and consider different learning strategies")
    if not recommendations:
        recommendations.append("Continue current study methods as they are working well")
    
    return DiagnosticReport(
        student_id=student.id,
        student_name=student.name,
        subject="All Subjects",  # Could be made more specific
        overall_percentage=round(overall_percentage, 2),
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        recent_performance=performance_records[:10],  # Last 10 records
        improvement_trend=improvement_trend
    )

@router.get("/student/my-performance")
def get_my_performance(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current student's own performance data"""
    if current_user.role != "student":
        raise HTTPException(status_code=403, detail="Student access required")
    
    # Get performance records
    performance_records = db.query(PerformanceRecord).filter(
        PerformanceRecord.student_id == current_user.id
    ).order_by(PerformanceRecord.created_at.desc()).all()
    
    # Calculate statistics
    total_assessments = len(performance_records)
    if total_assessments > 0:
        average_percentage = sum(record.percentage for record in performance_records) / total_assessments
        best_score = max(record.percentage for record in performance_records)
        recent_performance = performance_records[:5]  # Last 5 assessments
    else:
        average_percentage = 0
        best_score = 0
        recent_performance = []
    
    return {
        "total_assessments": total_assessments,
        "average_percentage": round(average_percentage, 2),
        "best_score": round(best_score, 2),
        "recent_performance": recent_performance
    }
