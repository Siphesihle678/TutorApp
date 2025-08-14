from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..core.auth import get_current_teacher, get_current_user
from ..models.user import User
from ..models.subject import Subject, Grade, StudentGrade
from ..schemas.subject import SubjectCreate, SubjectRead, SubjectUpdate, GradeCreate, GradeRead, StudentGradeCreate, StudentGradeRead

router = APIRouter()

# ==================== SUBJECT MANAGEMENT ====================

@router.post("/subjects", response_model=SubjectRead)
def create_subject(
    subject: SubjectCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Create a new subject for the current teacher"""
    db_subject = Subject(
        name=subject.name,
        description=subject.description,
        tutor_id=current_teacher.id
    )
    
    db.add(db_subject)
    db.commit()
    db.refresh(db_subject)
    
    return db_subject

@router.get("/subjects", response_model=List[SubjectRead])
def get_my_subjects(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get all subjects created by the current teacher"""
    subjects = db.query(Subject).filter(
        Subject.tutor_id == current_teacher.id,
        Subject.is_active == True
    ).all()
    
    return subjects

@router.get("/subjects/{subject_id}", response_model=SubjectRead)
def get_subject(
    subject_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get a specific subject by ID"""
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.tutor_id == current_teacher.id
    ).first()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    return subject

@router.put("/subjects/{subject_id}", response_model=SubjectRead)
def update_subject(
    subject_id: int,
    subject_update: SubjectUpdate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Update a subject"""
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.tutor_id == current_teacher.id
    ).first()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    if subject_update.name is not None:
        subject.name = subject_update.name
    if subject_update.description is not None:
        subject.description = subject_update.description
    if subject_update.is_active is not None:
        subject.is_active = subject_update.is_active
    
    db.commit()
    db.refresh(subject)
    
    return subject

@router.delete("/subjects/{subject_id}")
def delete_subject(
    subject_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Delete a subject (soft delete)"""
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.tutor_id == current_teacher.id
    ).first()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    subject.is_active = False
    db.commit()
    
    return {"message": "Subject deleted successfully"}

# ==================== GRADE MANAGEMENT ====================

@router.post("/subjects/{subject_id}/grades", response_model=GradeRead)
def create_grade(
    subject_id: int,
    grade: GradeCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Create a new grade for a subject"""
    # Verify the subject belongs to the teacher
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.tutor_id == current_teacher.id
    ).first()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    db_grade = Grade(
        name=grade.name,
        subject_id=subject_id
    )
    
    db.add(db_grade)
    db.commit()
    db.refresh(db_grade)
    
    return db_grade

@router.get("/subjects/{subject_id}/grades", response_model=List[GradeRead])
def get_subject_grades(
    subject_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get all grades for a subject"""
    # Verify the subject belongs to the teacher
    subject = db.query(Subject).filter(
        Subject.id == subject_id,
        Subject.tutor_id == current_teacher.id
    ).first()
    
    if not subject:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Subject not found"
        )
    
    grades = db.query(Grade).filter(
        Grade.subject_id == subject_id,
        Grade.is_active == True
    ).all()
    
    return grades

@router.get("/grades", response_model=List[GradeRead])
def get_all_grades(
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get all grades for all subjects of the current teacher"""
    grades = db.query(Grade).join(Subject).filter(
        Subject.tutor_id == current_teacher.id,
        Grade.is_active == True
    ).all()
    
    return grades

# ==================== STUDENT ENROLLMENT ====================

@router.post("/grades/{grade_id}/enroll", response_model=StudentGradeRead)
def enroll_student_in_grade(
    grade_id: int,
    enrollment: StudentGradeCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Enroll a student in a specific grade"""
    # Verify the grade belongs to the teacher
    grade = db.query(Grade).join(Subject).filter(
        Grade.id == grade_id,
        Subject.tutor_id == current_teacher.id
    ).first()
    
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    
    # Verify the student belongs to the teacher
    student = db.query(User).filter(
        User.id == enrollment.student_id,
        User.tutor_id == current_teacher.id,
        User.role == "student"
    ).first()
    
    if not student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student not found or not assigned to you"
        )
    
    # Check if already enrolled
    existing_enrollment = db.query(StudentGrade).filter(
        StudentGrade.student_id == enrollment.student_id,
        StudentGrade.grade_id == grade_id,
        StudentGrade.is_active == True
    ).first()
    
    if existing_enrollment:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student is already enrolled in this grade"
        )
    
    db_enrollment = StudentGrade(
        student_id=enrollment.student_id,
        grade_id=grade_id
    )
    
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    
    return db_enrollment

@router.get("/grades/{grade_id}/students", response_model=List[StudentGradeRead])
def get_grade_students(
    grade_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Get all students enrolled in a specific grade"""
    # Verify the grade belongs to the teacher
    grade = db.query(Grade).join(Subject).filter(
        Grade.id == grade_id,
        Subject.tutor_id == current_teacher.id
    ).first()
    
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    
    enrollments = db.query(StudentGrade).filter(
        StudentGrade.grade_id == grade_id,
        StudentGrade.is_active == True
    ).all()
    
    return enrollments

@router.delete("/grades/{grade_id}/unenroll/{student_id}")
def unenroll_student_from_grade(
    grade_id: int,
    student_id: int,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Unenroll a student from a grade"""
    # Verify the grade belongs to the teacher
    grade = db.query(Grade).join(Subject).filter(
        Grade.id == grade_id,
        Subject.tutor_id == current_teacher.id
    ).first()
    
    if not grade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Grade not found"
        )
    
    enrollment = db.query(StudentGrade).filter(
        StudentGrade.grade_id == grade_id,
        StudentGrade.student_id == student_id,
        StudentGrade.is_active == True
    ).first()
    
    if not enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Student enrollment not found"
        )
    
    enrollment.is_active = False
    db.commit()
    
    return {"message": "Student unenrolled successfully"}

