from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AssignmentBase(BaseModel):
    title: str
    description: str
    subject: str
    due_date: datetime
    max_points: float = 100.0
    is_active: bool = True

class AssignmentCreate(AssignmentBase):
    pass

class AssignmentRead(AssignmentBase):
    id: int
    creator_id: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class AssignmentSubmissionBase(BaseModel):
    content: str
    file_url: Optional[str] = None

class AssignmentSubmissionCreate(AssignmentSubmissionBase):
    assignment_id: int

class AssignmentSubmissionRead(AssignmentSubmissionBase):
    id: int
    assignment_id: int
    student_id: int
    submitted_at: datetime
    grade: Optional[float] = None
    feedback: Optional[str] = None

    class Config:
        from_attributes = True

class AssignmentGrade(BaseModel):
    submission_id: int
    grade: float
    feedback: Optional[str] = None
    graded_by: int
    graded_at: datetime = datetime.utcnow()

    class Config:
        from_attributes = True
