from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

# ==================== ASSIGNMENT SCHEMAS ====================

class AssignmentBase(BaseModel):
    title: str
    description: Optional[str] = None
    subject: str
    max_points: float = 100.0
    due_date: Optional[datetime] = None

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    subject: Optional[str] = None
    max_points: Optional[float] = None
    due_date: Optional[datetime] = None
    is_active: Optional[bool] = None

class AssignmentRead(AssignmentBase):
    id: int
    creator_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# ==================== ASSIGNMENT SUBMISSION SCHEMAS ====================

class AssignmentSubmissionBase(BaseModel):
    content: str

class AssignmentSubmissionCreate(AssignmentSubmissionBase):
    pass

class AssignmentSubmissionRead(AssignmentSubmissionBase):
    id: int
    assignment_id: int
    student_id: int
    submitted_at: datetime
    score: Optional[float] = None
    feedback: Optional[str] = None
    graded_at: Optional[datetime] = None
    graded_by: Optional[int] = None

    class Config:
        from_attributes = True

# ==================== ASSIGNMENT GRADING SCHEMAS ====================

class AssignmentGrade(BaseModel):
    grade: float
    feedback: Optional[str] = None

# ==================== ASSIGNMENT ANALYTICS SCHEMAS ====================

class AssignmentAnalytics(BaseModel):
    assignment_id: int
    total_submissions: int
    submitted_count: int
    graded_count: int
    average_score: float
    submission_rate: float
    late_submissions: int

# ==================== ASSIGNMENT DASHBOARD SCHEMAS ====================

class AssignmentSummary(BaseModel):
    id: int
    title: str
    subject: str
    due_date: Optional[datetime]
    submission_count: int
    is_active: bool
    created_at: datetime

class AssignmentOverview(BaseModel):
    total_assignments: int
    active_assignments: int
    total_submissions: int
    pending_grades: int
    recent_assignments: List[AssignmentSummary] = []

# ==================== ASSIGNMENT EXPORT SCHEMAS ====================

class AssignmentExport(BaseModel):
    assignment: AssignmentRead
    submissions: List[AssignmentSubmissionRead]
    analytics: AssignmentAnalytics

# ==================== ASSIGNMENT TEMPLATE SCHEMAS ====================

class AssignmentTemplate(BaseModel):
    name: str
    description: str
    subject: str
    estimated_points: float
    estimated_time: int  # in minutes
    difficulty_level: str  # "easy", "medium", "hard"

class AssignmentTemplateCreate(AssignmentTemplate):
    pass

class AssignmentTemplateRead(AssignmentTemplate):
    id: int
    created_by: int
    created_at: datetime
    usage_count: int = 0

    class Config:
        from_attributes = True
