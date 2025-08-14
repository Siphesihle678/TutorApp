from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class GradeBase(BaseModel):
    name: str

class GradeCreate(GradeBase):
    pass

class GradeRead(GradeBase):
    id: int
    subject_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True

class SubjectBase(BaseModel):
    name: str
    description: Optional[str] = None

class SubjectCreate(SubjectBase):
    pass

class SubjectRead(SubjectBase):
    id: int
    tutor_id: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime]
    grades: List[GradeRead] = []
    
    class Config:
        from_attributes = True

class SubjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None

class StudentGradeCreate(BaseModel):
    student_id: int
    grade_id: int

class StudentGradeRead(BaseModel):
    id: int
    student_id: int
    grade_id: int
    enrolled_at: datetime
    is_active: bool
    grade: GradeRead
    
    class Config:
        from_attributes = True

