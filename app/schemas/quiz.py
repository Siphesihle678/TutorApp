from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from ..models.quiz import QuestionType

class QuestionBase(BaseModel):
    text: str
    question_type: QuestionType
    options: Optional[List[str]] = None
    correct_answer: str
    points: float = 1.0
    explanation: Optional[str] = None

class QuestionCreate(QuestionBase):
    pass

class QuestionRead(QuestionBase):
    id: int
    quiz_id: int
    
    class Config:
        from_attributes = True

class QuizBase(BaseModel):
    title: str
    description: Optional[str] = None
    subject: str
    time_limit: Optional[int] = None
    passing_score: float = 60.0

class QuizCreate(QuizBase):
    questions: List[QuestionCreate]

class QuizRead(QuizBase):
    id: int
    creator_id: int
    is_active: bool
    created_at: datetime
    questions: List[QuestionRead]
    
    class Config:
        from_attributes = True

class QuizAttemptCreate(BaseModel):
    quiz_id: int

class QuizAttemptRead(BaseModel):
    id: int
    quiz_id: int
    student_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    is_passed: Optional[bool] = None
    time_taken: Optional[int] = None
    
    class Config:
        from_attributes = True

class QuizSubmissionCreate(BaseModel):
    question_id: int
    answer: str

class QuizResult(BaseModel):
    attempt_id: int
    score: float
    max_score: float
    percentage: float
    is_passed: bool
    time_taken: int
    question_results: List[Dict[str, Any]]
