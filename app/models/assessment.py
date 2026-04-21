from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class FormalAssessment(Base):
    __tablename__ = "formal_assessments"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=True)
    grade_id = Column(Integer, ForeignKey("grades.id"), nullable=True)
    
    # Timing
    due_date = Column(DateTime(timezone=True), nullable=False)
    time_limit_minutes = Column(Integer, default=120)  # 2 Hours strict
    strict_lockdown = Column(Boolean, default=True)
    
    # Files array (Multiple elements for pre-requisite downloads: .docx, .accdb)
    data_files = Column(JSON, default=list) 
    
    max_points = Column(Float, default=100.0)
    is_active = Column(Boolean, default=True)
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    creator = relationship("User", back_populates="formal_assessments_created")
    submissions = relationship("FormalSubmission", back_populates="assessment", cascade="all, delete-orphan")

class FormalSubmission(Base):
    __tablename__ = "formal_submissions"
    
    id = Column(Integer, primary_key=True, index=True)
    assessment_id = Column(Integer, ForeignKey("formal_assessments.id"), nullable=False)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Timer Hooks to enforce lockdown
    started_at = Column(DateTime(timezone=True), nullable=False)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Dual Output
    text_responses = Column(JSON, default=dict)    # Text rationales 
    uploaded_files = Column(JSON, default=list)    # Final .accdb or .xlsx pushed by student
    
    # Formatting
    ai_suggested_score = Column(Float, nullable=True)
    ai_feedback_log = Column(Text, nullable=True)
    
    final_score = Column(Float, nullable=True)
    teacher_feedback = Column(Text, nullable=True)
    
    # Relationships
    assessment = relationship("FormalAssessment", back_populates="submissions")
    student = relationship("User", back_populates="formal_submissions")
