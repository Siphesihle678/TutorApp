from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class PerformanceRecord(Base):
    __tablename__ = "performance_records"
    
    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String, nullable=False)
    assessment_type = Column(String, nullable=False)  # quiz, assignment, etc.
    assessment_id = Column(Integer, nullable=False)  # ID of quiz or assignment
    score = Column(Float, nullable=False)
    max_score = Column(Float, nullable=False)
    percentage = Column(Float, nullable=False)
    time_taken = Column(Integer)  # in seconds
    strengths = Column(JSON)  # List of strong areas
    weaknesses = Column(JSON)  # List of areas needing improvement
    recommendations = Column(Text)  # Personalized recommendations
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Foreign Keys
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    student = relationship("User", back_populates="performance_records")
