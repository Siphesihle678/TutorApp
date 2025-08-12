from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime

class PerformanceRecordRead(BaseModel):
    id: int
    student_id: int
    subject: str
    assessment_type: str
    assessment_id: int
    score: float
    max_score: float
    percentage: float
    time_taken: Optional[int] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    recommendations: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True

class StudentPerformance(BaseModel):
    student_id: int
    student_name: str
    total_quizzes: int
    total_assignments: int
    average_quiz_score: float
    average_assignment_score: float
    overall_percentage: float
    rank: Optional[int] = None

class LeaderboardEntry(BaseModel):
    rank: int
    student_id: int
    student_name: str
    total_score: float
    total_assessments: int
    average_percentage: float

class DiagnosticReport(BaseModel):
    student_id: int
    student_name: str
    subject: str
    overall_percentage: float
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    recent_performance: List[PerformanceRecordRead]
    improvement_trend: str  # "improving", "declining", "stable"
