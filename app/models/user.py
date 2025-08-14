from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
from ..core.database import Base

class UserRole(str, enum.Enum):
    TEACHER = "teacher"
    STUDENT = "student"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(Enum(UserRole), default=UserRole.STUDENT, nullable=False)
    tutor_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)  # Links student to their tutor
    tutor_code = Column(String, unique=True, nullable=True, index=True)  # Unique code for tutor assignment
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    quizzes_created = relationship("Quiz", back_populates="creator")
    quiz_attempts = relationship("QuizAttempt", back_populates="student")
    assignments_created = relationship("Assignment", back_populates="creator")
    assignment_submissions = relationship("AssignmentSubmission", back_populates="student")
    announcements_created = relationship("Announcement", back_populates="creator")
    performance_records = relationship("PerformanceRecord", back_populates="student")
    
    # Subject/Grade relationships (commented out to avoid import issues)
    # subjects_created = relationship("Subject", back_populates="tutor")
    # enrolled_grades = relationship("StudentGrade", back_populates="student")
    
    # Tutor-Student relationships
    tutor = relationship("User", foreign_keys=[tutor_id], remote_side=[id], backref="students", lazy="joined")
