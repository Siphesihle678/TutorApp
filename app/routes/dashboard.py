from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_
from typing import List, Optional
from datetime import datetime, timedelta
from ..core.database import get_db
from ..core.auth import get_current_teacher, get_current_user, get_current_student
from ..models.user import User
from ..models.quiz import Quiz, QuizAttempt
from ..models.assignment import Assignment, AssignmentSubmission
from ..models.performance import PerformanceRecord
from ..schemas.performance import StudentPerformance, LeaderboardEntry, DiagnosticReport
from ..schemas.dashboard import (
    TeacherDashboard, StudentDashboard, 
    PerformanceAnalytics, SubjectAnalytics,
    TimeSeriesData, ProgressReport
)

router = APIRouter()

# ==================== DEBUG ENDPOINTS ====================

@router.get("/test")
def test_dashboard():
    """Simple test endpoint to verify dashboard routing"""
    return {
        "message": "Dashboard router is working!",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat()
    }

@router.get("/stats")
def get_dashboard_stats(db: Session = Depends(get_db)):
    """Get general dashboard statistics"""
    try:
        # Count total users
        total_users = db.query(User).count()
        total_students = db.query(User).filter(User.role == "student").count()
        total_teachers = db.query(User).filter(User.role == "teacher").count()
        
        # Count content
        total_quizzes = db.query(Quiz).count()
        total_assignments = db.query(Assignment).count()
        total_announcements = db.query(Announcement).count()
        
        # Count activity
        total_quiz_attempts = db.query(QuizAttempt).count()
        total_assignment_submissions = db.query(AssignmentSubmission).count()
        
        return {
            "status": "success",
            "stats": {
                "users": {
                    "total": total_users,
                    "students": total_students,
                    "teachers": total_teachers
                },
                "content": {
                    "quizzes": total_quizzes,
                    "assignments": total_assignments,
                    "announcements": total_announcements
                },
                "activity": {
                    "quiz_attempts": total_quiz_attempts,
                    "assignment_submissions": total_assignment_submissions
                }
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }

@router.get("/debug/students")
def debug_students(db: Session = Depends(get_db)):
    """Debug endpoint to check student data"""
    try:
        # Get all users
        all_users = db.query(User).all()
        
        # Get students specifically
        students = db.query(User).filter(User.role == "student").all()
        active_students = db.query(User).filter(User.role == "student", User.is_active == True).all()
        
        return {
            "total_users": len(all_users),
            "total_students": len(students),
            "active_students": len(active_students),
            "all_users": [
                {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email,
                    "role": user.role,
                    "is_active": user.is_active,
                    "created_at": user.created_at
                }
                for user in all_users
            ],
            "students": [
                {
                    "id": student.id,
                    "name": student.name,
                    "email": student.email,
                    "is_active": student.is_active,
                    "created_at": student.created_at
                }
                for student in students
            ],
            "active_students": [
                {
                    "id": student.id,
                    "name": student.name,
                    "email": student.email,
                    "created_at": student.created_at
                }
                for student in active_students
            ]
        }
    except Exception as e:
        return {
            "error": str(e),
            "error_type": type(e).__name__
        }

# ==================== TUTOR MANAGEMENT ====================

@router.get("/teacher/available-tutors")
def get_available_tutors(db: Session = Depends(get_db)):
    """Get list of available tutors for assignment"""
    tutors = db.query(User).filter(
        User.role == "teacher",
        User.is_active == True
    ).all()
    
    return [
        {
            "id": tutor.id,
            "name": tutor.name,
            "email": tutor.email,
            "student_count": len(tutor.students) if tutor.students else 0
        }
        for tutor in tutors
    ]

@router.get("/teacher/my-students")
def get_my_students(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get list of students assigned to current teacher"""
    students = db.query(User).filter(
        User.role == "student",
        User.tutor_id == current_teacher.id,
        User.is_active == True
    ).all()
    
    return [
        {
            "id": student.id,
            "name": student.name,
            "email": student.email,
            "created_at": student.created_at,
            "is_active": student.is_active
        }
        for student in students
    ]

@router.post("/teacher/assign-student/{student_id}")
def assign_student_to_tutor(
    student_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Assign a student to the current teacher"""
    # Check if student exists and is not already assigned
    student = db.query(User).filter(
        User.id == student_id,
        User.role == "student",
        User.is_active == True
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found"
        )
    
    if student.tutor_id == current_teacher.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is already assigned to you"
        )
    
    # Update student's tutor assignment
    student.tutor_id = current_teacher.id
    db.commit()
    db.refresh(student)
    
    return {
        "message": f"Student {student.name} successfully assigned to you",
        "student": {
            "id": student.id,
            "name": student.name,
            "email": student.email
        }
    }

@router.delete("/teacher/unassign-student/{student_id}")
def unassign_student_from_tutor(
    student_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Unassign a student from the current teacher"""
    # Check if student exists and is assigned to current teacher
    student = db.query(User).filter(
        User.id == student_id,
        User.role == "student",
        User.tutor_id == current_teacher.id,
        User.is_active == True
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found or not assigned to you"
        )
    
    # Remove tutor assignment
    student.tutor_id = None
    db.commit()
    db.refresh(student)
    
    return {
        "message": f"Student {student.name} successfully unassigned from you",
        "student": {
            "id": student.id,
            "name": student.name,
            "email": student.email
        }
    }

# ==================== TEACHER DASHBOARD ====================

@router.get("/teacher/overview", response_model=TeacherDashboard)
def get_teacher_overview(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get comprehensive teacher dashboard overview"""
    try:
        print(f"=== TEACHER DASHBOARD DEBUG ===")
        print(f"Teacher ID: {current_teacher.id}")
        print(f"Teacher Name: {current_teacher.name}")
        print(f"Teacher Role: {current_teacher.role}")
        
        # Debug: Check all users in the database
        all_users = db.query(User).all()
        print(f"Total users in database: {len(all_users)}")
        for user in all_users:
            print(f"User: ID={user.id}, Name={user.name}, Email={user.email}, Role={user.role}, Active={user.is_active}")
        
        # Count students with debugging - filter by tutor
        students_query = db.query(User).filter(
            User.role == "student", 
            User.is_active == True,
            User.tutor_id == current_teacher.id
        )
        print(f"Student query filter: role='student' AND is_active=True AND tutor_id={current_teacher.id}")
        
        # Check each condition separately
        all_students = db.query(User).filter(User.role == "student").all()
        print(f"Users with role='student': {len(all_students)}")
        for student in all_students:
            print(f"Student: ID={student.id}, Name={student.name}, Active={student.is_active}, Tutor ID={student.tutor_id}")
        
        active_students = db.query(User).filter(User.is_active == True).all()
        print(f"Users with is_active=True: {len(active_students)}")
        for user in active_students:
            print(f"Active user: ID={user.id}, Name={user.name}, Role={user.role}")
        
        my_students = db.query(User).filter(
            User.role == "student",
            User.tutor_id == current_teacher.id
        ).all()
        print(f"My students: {len(my_students)}")
        for student in my_students:
            print(f"My student: ID={student.id}, Name={student.name}, Active={student.is_active}")
        
        total_students = students_query.count()
        print(f"Final student count: {total_students}")
        
        # Count active quizzes and assignments
        total_quizzes = db.query(Quiz).filter(
            Quiz.creator_id == current_teacher.id,
            Quiz.is_active == True
        ).count()
        
        total_assignments = db.query(Assignment).filter(
            Assignment.creator_id == current_teacher.id,
            Assignment.is_active == True
        ).count()
        
        # Count recent submissions - simplified without joins
        try:
            recent_quiz_attempts = db.query(QuizAttempt).filter(
                QuizAttempt.quiz_id.in_(
                    db.query(Quiz.id).filter(Quiz.creator_id == current_teacher.id)
                ),
                QuizAttempt.completed_at != None
            ).count()
        except Exception as quiz_error:
            print(f"Quiz attempts calculation error: {quiz_error}")
            recent_quiz_attempts = 0
            
        try:
            recent_assignment_submissions = db.query(AssignmentSubmission).filter(
                AssignmentSubmission.assignment_id.in_(
                    db.query(Assignment.id).filter(Assignment.creator_id == current_teacher.id)
                )
            ).count()
        except Exception as assign_error:
            print(f"Assignment submissions calculation error: {assign_error}")
            recent_assignment_submissions = 0
        
        # Calculate average performance - simplified without join
        try:
            avg_performance = db.query(func.avg(PerformanceRecord.percentage)).filter(
                PerformanceRecord.quiz_id.in_(
                    db.query(Quiz.id).filter(Quiz.creator_id == current_teacher.id)
                )
            ).scalar() or 0
        except Exception as perf_error:
            print(f"Performance calculation error: {perf_error}")
            avg_performance = 0
        
        # Simplified response without helper functions
        result = {
            "total_students": total_students,
            "total_quizzes": total_quizzes,
            "total_assignments": total_assignments,
            "recent_quiz_attempts": recent_quiz_attempts,
            "recent_assignment_submissions": recent_assignment_submissions,
            "average_performance": round(avg_performance, 2),
            "recent_activity": [],  # Simplified - empty array
            "subject_breakdown": {}  # Simplified - empty object
        }
        
        print(f"=== DASHBOARD SUMMARY ===")
        print(f"Total students: {total_students}")
        print(f"Total quizzes: {total_quizzes}")
        print(f"Total assignments: {total_assignments}")
        print(f"Result: {result}")
        
        return result
        
    except Exception as e:
        print(f"=== TEACHER DASHBOARD ERROR ===")
        print(f"Error type: {type(e).__name__}")
        print(f"Error message: {str(e)}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        raise

@router.get("/teacher/students", response_model=List[StudentPerformance])
def get_student_performances(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db),
    subject: Optional[str] = None
):
    """Get detailed student performance data"""
    query = db.query(User).filter(
        User.role == "student", 
        User.is_active == True,
        User.tutor_id == current_teacher.id
    )
    
    if subject:
        # Filter by subject if specified
        query = query.join(PerformanceRecord).filter(PerformanceRecord.subject == subject)
    
    students = query.all()
    
    performances = []
    for student in students:
        # Get student's performance records
        performance_records = db.query(PerformanceRecord).filter(
            PerformanceRecord.student_id == student.id
        ).all()
        
        if not performance_records:
            continue
        
        # Calculate statistics
        total_assessments = len(performance_records)
        average_percentage = sum(r.percentage for r in performance_records) / total_assessments
        best_score = max(r.percentage for r in performance_records)
        worst_score = min(r.percentage for r in performance_records)
        
        # Get recent performance trend
        recent_records = sorted(performance_records, key=lambda x: x.created_at, reverse=True)[:5]
        recent_average = sum(r.percentage for r in recent_records) / len(recent_records)
        
        # Get subject breakdown
        subject_performance = {}
        for record in performance_records:
            if record.subject not in subject_performance:
                subject_performance[record.subject] = []
            subject_performance[record.subject].append(record.percentage)
        
        subject_averages = {
            subject: sum(scores) / len(scores) 
            for subject, scores in subject_performance.items()
        }
        
        performances.append(StudentPerformance(
            student_id=student.id,
            student_name=student.name,
            student_email=student.email,
            total_assessments=total_assessments,
            average_percentage=round(average_percentage, 2),
            best_score=round(best_score, 2),
            worst_score=round(worst_score, 2),
            recent_trend=round(recent_average, 2),
            subject_breakdown=subject_averages,
            last_assessment=performance_records[-1].created_at if performance_records else None
        ))
    
    return sorted(performances, key=lambda x: x.average_percentage, reverse=True)

@router.get("/teacher/analytics", response_model=PerformanceAnalytics)
def get_performance_analytics(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db),
    days: int = 30
):
    """Get detailed performance analytics"""
    start_date = datetime.utcnow() - timedelta(days=days)
    
    # Get performance records for teacher's content
    performance_records = db.query(PerformanceRecord).join(Quiz).filter(
        Quiz.creator_id == current_teacher.id,
        PerformanceRecord.created_at >= start_date
    ).all()
    
    if not performance_records:
        return {
            "total_assessments": 0,
            "average_performance": 0,
            "performance_trend": [],
            "subject_analytics": [],
            "difficulty_analysis": {}
        }
    
    # Calculate overall statistics
    total_assessments = len(performance_records)
    average_performance = sum(r.percentage for r in performance_records) / total_assessments
    
    # Get performance trend over time
    performance_trend = get_performance_trend(performance_records, days)
    
    # Get subject analytics
    subject_analytics = get_subject_analytics(performance_records)
    
    # Get difficulty analysis
    difficulty_analysis = get_difficulty_analysis(performance_records)
    
    return {
        "total_assessments": total_assessments,
        "average_performance": round(average_performance, 2),
        "performance_trend": performance_trend,
        "subject_analytics": subject_analytics,
        "difficulty_analysis": difficulty_analysis
    }

# ==================== STUDENT DASHBOARD ====================

@router.get("/student/overview", response_model=StudentDashboard)
def get_student_overview(
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get comprehensive student dashboard overview"""
    # Get student's performance records
    performance_records = db.query(PerformanceRecord).filter(
        PerformanceRecord.student_id == current_student.id
    ).all()
    
    if not performance_records:
        return {
            "total_assessments": 0,
            "average_percentage": 0,
            "best_score": 0,
            "current_rank": 0,
            "recent_performance": [],
            "subject_breakdown": {},
            "upcoming_deadlines": []
        }
    
    # Calculate basic statistics
    total_assessments = len(performance_records)
    average_percentage = sum(r.percentage for r in performance_records) / total_assessments
    best_score = max(r.percentage for r in performance_records)
    
    # Get current rank
    current_rank = get_student_rank(current_student.id, db)
    
    # Get recent performance
    recent_performance = sorted(performance_records, key=lambda x: x.created_at, reverse=True)[:10]
    
    # Get subject breakdown
    subject_breakdown = {}
    for record in performance_records:
        if record.subject not in subject_breakdown:
            subject_breakdown[record.subject] = []
        subject_breakdown[record.subject].append(record.percentage)
    
    subject_averages = {
        subject: round(sum(scores) / len(scores), 2)
        for subject, scores in subject_breakdown.items()
    }
    
    # Get upcoming deadlines
    upcoming_deadlines = get_upcoming_deadlines(current_student.id, db)
    
    return {
        "total_assessments": total_assessments,
        "average_percentage": round(average_percentage, 2),
        "best_score": round(best_score, 2),
        "current_rank": current_rank,
        "recent_performance": [
            {
                "assessment_type": r.assessment_type,
                "subject": r.subject,
                "score": r.score,
                "max_score": r.max_score,
                "percentage": r.percentage,
                "date": r.created_at
            }
            for r in recent_performance
        ],
        "subject_breakdown": subject_averages,
        "upcoming_deadlines": upcoming_deadlines
    }

@router.get("/student/my-performance", response_model=DiagnosticReport)
def get_student_performance(
    current_student: User = Depends(get_current_student),
    db: Session = Depends(get_db)
):
    """Get detailed student performance report"""
    performance_records = db.query(PerformanceRecord).filter(
        PerformanceRecord.student_id == current_student.id
    ).all()
    
    if not performance_records:
        return {
            "total_assessments": 0,
            "average_percentage": 0,
            "best_score": 0,
            "strengths": [],
            "weaknesses": [],
            "recommendations": ["Start taking assessments to track your progress"],
            "recent_performance": []
        }
    
    # Calculate statistics
    total_assessments = len(performance_records)
    average_percentage = sum(r.percentage for r in performance_records) / total_assessments
    best_score = max(r.percentage for r in performance_records)
    
    # Analyze strengths and weaknesses
    strengths, weaknesses = analyze_performance(performance_records)
    
    # Generate recommendations
    recommendations = generate_recommendations(performance_records, average_percentage)
    
    # Get recent performance
    recent_performance = sorted(performance_records, key=lambda x: x.created_at, reverse=True)[:5]
    
    return {
        "total_assessments": total_assessments,
        "average_percentage": round(average_percentage, 2),
        "best_score": round(best_score, 2),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "recommendations": recommendations,
        "recent_performance": [
            {
                "assessment_type": r.assessment_type,
                "subject": r.subject,
                "score": r.score,
                "max_score": r.max_score,
                "percentage": r.percentage,
                "date": r.created_at
            }
            for r in recent_performance
        ]
    }

# ==================== LEADERBOARD ====================

@router.get("/leaderboard", response_model=List[LeaderboardEntry])
def get_leaderboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    subject: Optional[str] = None,
    limit: int = 10
):
    """Get class leaderboard"""
    # Get students based on user role
    if current_user.role == "teacher":
        # Teachers see only their students
        students = db.query(User).filter(
            User.role == "student", 
            User.is_active == True,
            User.tutor_id == current_user.id
        ).all()
    else:
        # Students see all students (or could be filtered by their tutor's students)
        students = db.query(User).filter(User.role == "student", User.is_active == True).all()
    
    leaderboard_entries = []
    for student in students:
        # Get student's performance records
        query = db.query(PerformanceRecord).filter(PerformanceRecord.student_id == student.id)
        
        if subject:
            query = query.filter(PerformanceRecord.subject == subject)
        
        performance_records = query.all()
        
        if not performance_records:
            continue
        
        # Calculate total score and average
        total_score = sum(r.score for r in performance_records)
        total_assessments = len(performance_records)
        average_percentage = sum(r.percentage for r in performance_records) / total_assessments
        
        leaderboard_entries.append(LeaderboardEntry(
            rank=0,  # Will be calculated after sorting
            student_id=student.id,
            student_name=student.name,
            total_score=total_score,
            total_assessments=total_assessments,
            average_percentage=round(average_percentage, 2)
        ))
    
    # Sort by average percentage and assign ranks
    leaderboard_entries.sort(key=lambda x: x.average_percentage, reverse=True)
    
    for i, entry in enumerate(leaderboard_entries[:limit]):
        entry.rank = i + 1
    
    return leaderboard_entries[:limit]

# ==================== HELPER FUNCTIONS ====================

def get_recent_activity(teacher_id: int, db: Session) -> List[dict]:
    """Get recent activity for teacher dashboard"""
    # Get recent quiz attempts
    recent_quiz_attempts = db.query(QuizAttempt).join(Quiz).filter(
        Quiz.creator_id == teacher_id,
        QuizAttempt.completed_at != None
    ).order_by(desc(QuizAttempt.completed_at)).limit(5).all()
    
    # Get recent assignment submissions
    recent_submissions = db.query(AssignmentSubmission).join(Assignment).filter(
        Assignment.creator_id == teacher_id
    ).order_by(desc(AssignmentSubmission.submitted_at)).limit(5).all()
    
    activity = []
    
    for attempt in recent_quiz_attempts:
        activity.append({
            "type": "quiz_attempt",
            "student_name": attempt.student.name,
            "quiz_title": attempt.quiz.title,
            "score": attempt.score,
            "date": attempt.completed_at
        })
    
    for submission in recent_submissions:
        activity.append({
            "type": "assignment_submission",
            "student_name": submission.student.name,
            "assignment_title": submission.assignment.title,
            "date": submission.submitted_at
        })
    
    # Sort by date
    activity.sort(key=lambda x: x["date"], reverse=True)
    return activity[:10]

def get_subject_breakdown(teacher_id: int, db: Session) -> dict:
    """Get subject breakdown for teacher dashboard"""
    # Get all quizzes and assignments by subject
    quizzes = db.query(Quiz).filter(Quiz.creator_id == teacher_id).all()
    assignments = db.query(Assignment).filter(Assignment.creator_id == teacher_id).all()
    
    subject_counts = {}
    
    for quiz in quizzes:
        if quiz.subject not in subject_counts:
            subject_counts[quiz.subject] = {"quizzes": 0, "assignments": 0}
        subject_counts[quiz.subject]["quizzes"] += 1
    
    for assignment in assignments:
        if assignment.subject not in subject_counts:
            subject_counts[assignment.subject] = {"quizzes": 0, "assignments": 0}
        subject_counts[assignment.subject]["assignments"] += 1
    
    return subject_counts

def get_performance_trend(performance_records: List[PerformanceRecord], days: int) -> List[dict]:
    """Get performance trend over time"""
    # Group by date and calculate daily averages
    daily_performance = {}
    
    for record in performance_records:
        date_key = record.created_at.date()
        if date_key not in daily_performance:
            daily_performance[date_key] = []
        daily_performance[date_key].append(record.percentage)
    
    # Calculate daily averages
    trend_data = []
    for date, percentages in sorted(daily_performance.items()):
        trend_data.append({
            "date": date,
            "average_percentage": round(sum(percentages) / len(percentages), 2),
            "count": len(percentages)
        })
    
    return trend_data

def get_subject_analytics(performance_records: List[PerformanceRecord]) -> List[dict]:
    """Get analytics by subject"""
    subject_data = {}
    
    for record in performance_records:
        if record.subject not in subject_data:
            subject_data[record.subject] = []
        subject_data[record.subject].append(record.percentage)
    
    analytics = []
    for subject, percentages in subject_data.items():
        analytics.append({
            "subject": subject,
            "average_percentage": round(sum(percentages) / len(percentages), 2),
            "total_assessments": len(percentages),
            "best_score": max(percentages),
            "worst_score": min(percentages)
        })
    
    return analytics

def get_difficulty_analysis(performance_records: List[PerformanceRecord]) -> dict:
    """Analyze performance by difficulty level"""
    # Categorize by performance level
    easy = [r for r in performance_records if r.percentage >= 80]
    medium = [r for r in performance_records if 60 <= r.percentage < 80]
    hard = [r for r in performance_records if r.percentage < 60]
    
    return {
        "easy": {
            "count": len(easy),
            "average": round(sum(r.percentage for r in easy) / len(easy), 2) if easy else 0
        },
        "medium": {
            "count": len(medium),
            "average": round(sum(r.percentage for r in medium) / len(medium), 2) if medium else 0
        },
        "hard": {
            "count": len(hard),
            "average": round(sum(r.percentage for r in hard) / len(hard), 2) if hard else 0
        }
    }

def get_student_rank(student_id: int, db: Session) -> int:
    """Get student's current rank in class"""
    # Get all students with their average performance
    students = db.query(User).filter(User.role == "student", User.is_active == True).all()
    
    student_averages = []
    for student in students:
        performance_records = db.query(PerformanceRecord).filter(
            PerformanceRecord.student_id == student.id
        ).all()
        
        if performance_records:
            average = sum(r.percentage for r in performance_records) / len(performance_records)
            student_averages.append((student.id, average))
    
    # Sort by average and find rank
    student_averages.sort(key=lambda x: x[1], reverse=True)
    
    for i, (sid, _) in enumerate(student_averages):
        if sid == student_id:
            return i + 1
    
    return 0

def get_upcoming_deadlines(student_id: int, db: Session) -> List[dict]:
    """Get upcoming assignment deadlines for student"""
    # Get active assignments with due dates
    assignments = db.query(Assignment).filter(
        Assignment.is_active == True,
        Assignment.due_date != None,
        Assignment.due_date > datetime.utcnow()
    ).all()
    
    deadlines = []
    for assignment in assignments:
        # Check if student has already submitted
        submission = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.assignment_id == assignment.id,
            AssignmentSubmission.student_id == student_id
        ).first()
        
        if not submission:
            deadlines.append({
                "assignment_id": assignment.id,
                "title": assignment.title,
                "subject": assignment.subject,
                "due_date": assignment.due_date,
                "days_remaining": (assignment.due_date - datetime.utcnow()).days
            })
    
    return sorted(deadlines, key=lambda x: x["due_date"])

def analyze_performance(performance_records: List[PerformanceRecord]) -> tuple:
    """Analyze student performance to identify strengths and weaknesses"""
    strengths = []
    weaknesses = []
    
    # Analyze by subject
    subject_performance = {}
    for record in performance_records:
        if record.subject not in subject_performance:
            subject_performance[record.subject] = []
        subject_performance[record.subject].append(record.percentage)
    
    for subject, percentages in subject_performance.items():
        average = sum(percentages) / len(percentages)
        if average >= 75:
            strengths.append(f"Strong performance in {subject}")
        elif average < 60:
            weaknesses.append(f"Needs improvement in {subject}")
    
    # Analyze recent trend
    recent_records = sorted(performance_records, key=lambda x: x.created_at, reverse=True)[:5]
    if len(recent_records) >= 3:
        recent_average = sum(r.percentage for r in recent_records) / len(recent_records)
        if recent_average > 80:
            strengths.append("Showing consistent improvement")
        elif recent_average < 60:
            weaknesses.append("Recent performance needs attention")
    
    return strengths, weaknesses

def generate_recommendations(performance_records: List[PerformanceRecord], average_percentage: float) -> List[str]:
    """Generate personalized recommendations"""
    recommendations = []
    
    if average_percentage >= 85:
        recommendations.append("Excellent work! Consider helping classmates or taking advanced challenges.")
    elif average_percentage >= 70:
        recommendations.append("Good progress! Focus on areas where you scored below 70%.")
    elif average_percentage >= 60:
        recommendations.append("You're on the right track. Review concepts where you struggled.")
    else:
        recommendations.append("Consider reviewing fundamental concepts and seeking additional help.")
    
    # Subject-specific recommendations
    subject_performance = {}
    for record in performance_records:
        if record.subject not in subject_performance:
            subject_performance[record.subject] = []
        subject_performance[record.subject].append(record.percentage)
    
    for subject, percentages in subject_performance.items():
        subject_average = sum(percentages) / len(percentages)
        if subject_average < 60:
            recommendations.append(f"Focus on improving your {subject} skills through practice.")
    
    return recommendations
