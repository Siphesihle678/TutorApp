from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum

class QuestionType(str, Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    TRUE_FALSE = "true_false"
    SHORT_ANSWER = "short_answer"
    ESSAY = "essay"

# ==================== QUIZ SCHEMAS ====================

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

class QuizUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    time_limit: Optional[int] = None
    passing_score: Optional[float] = None
    is_active: Optional[bool] = None

class QuizRead(QuizBase):
    id: int
    creator_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    questions: List[QuestionRead] = []

    class Config:
        from_attributes = True

# ==================== QUIZ ATTEMPT SCHEMAS ====================

class QuizAttemptBase(BaseModel):
    quiz_id: int

class QuizAttemptCreate(QuizAttemptBase):
    id: int
    student_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    is_passed: Optional[bool] = None
    time_taken: Optional[int] = None

    class Config:
        from_attributes = True

class QuizAttemptRead(QuizAttemptBase):
    id: int
    student_id: int
    started_at: datetime
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    is_passed: Optional[bool] = None
    time_taken: Optional[int] = None

    class Config:
        from_attributes = True

# ==================== QUIZ SUBMISSION SCHEMAS ====================

class QuizSubmissionBase(BaseModel):
    question_id: int
    answer: str

class QuizSubmissionCreate(QuizSubmissionBase):
    pass

class QuizSubmissionRead(QuizSubmissionBase):
    id: int
    attempt_id: int
    is_correct: Optional[bool] = None
    points_earned: float = 0.0
    submitted_at: datetime

    class Config:
        from_attributes = True

# ==================== QUIZ RESULT SCHEMAS ====================

class QuizResult(BaseModel):
    attempt_id: int
    score: float
    max_score: float
    percentage: float
    is_passed: bool
    time_taken: int
    question_results: List[Dict[str, Any]] = []

# ==================== QUIZ ANALYTICS SCHEMAS ====================

class QuestionAnalytics(BaseModel):
    question_id: int
    question_text: str
    success_rate: float
    total_attempts: int

class QuizAnalytics(BaseModel):
    quiz_id: int
    total_attempts: int
    average_score: float
    pass_rate: float
    average_time: float
    question_analytics: List[QuestionAnalytics] = []

# ==================== QUIZ DASHBOARD SCHEMAS ====================

class QuizSummary(BaseModel):
    id: int
    title: str
    subject: str
    total_attempts: int
    average_score: float
    pass_rate: float
    is_active: bool
    created_at: datetime

class StudentQuizPerformance(BaseModel):
    student_id: int
    student_name: str
    student_email: str
    total_quizzes_taken: int
    average_score: float
    best_score: float
    total_time_spent: int  # in minutes
    last_quiz_date: Optional[datetime] = None

# ==================== QUIZ EXPORT SCHEMAS ====================

class QuizExport(BaseModel):
    quiz: QuizRead
    attempts: List[QuizAttemptRead]
    submissions: List[QuizSubmissionRead]
    analytics: QuizAnalytics

# ==================== QUIZ TEMPLATE SCHEMAS ====================

class QuizTemplate(BaseModel):
    name: str
    description: str
    subject: str
    questions: List[QuestionCreate]
    estimated_time: int  # in minutes
    difficulty_level: str  # "easy", "medium", "hard"

class QuizTemplateCreate(QuizTemplate):
    pass

class QuizTemplateRead(QuizTemplate):
    id: int
    created_by: int
    created_at: datetime
    usage_count: int = 0

    class Config:
        from_attributes = True
