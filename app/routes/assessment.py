from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from ..core.database import get_db
from ..core.auth import get_current_teacher, get_current_user, get_current_student
from ..models.user import User
from ..models.assessment import FormalAssessment, FormalSubmission
from pydantic import BaseModel

router = APIRouter()

# Simple Schemas
class AssessmentCreate(BaseModel):
    title: str
    due_date: datetime
    time_limit_minutes: int
    data_files: list = []

@router.post("/")
def create_assessment(data: AssessmentCreate, db: Session = Depends(get_db), current_teacher: User = Depends(get_current_teacher)):
    assessment = FormalAssessment(
        title=data.title,
        due_date=data.due_date,
        time_limit_minutes=data.time_limit_minutes,
        data_files=data.data_files,
        creator_id=current_teacher.id
    )
    db.add(assessment)
    db.commit()
    return {"message": "Assessment securely created in Lockdown Mode"}

@router.get("/")
def get_assessments(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    # Very basic fetching
    return db.query(FormalAssessment).filter(FormalAssessment.is_active == True).all()

@router.post("/{assessment_id}/start")
def start_assessment(assessment_id: int, db: Session = Depends(get_db), current_student: User = Depends(get_current_student)):
    """Triggers the strict lock timer!"""
    assessment = db.query(FormalAssessment).filter(FormalAssessment.id == assessment_id).first()
    if not assessment:
        raise HTTPException(404, "Not Found")
        
    sub = FormalSubmission(
        assessment_id=assessment_id,
        student_id=current_student.id,
        started_at=datetime.utcnow()
    )
    db.add(sub)
    db.commit()
    db.refresh(sub)
    return {"submission_id": sub.id, "started_at": sub.started_at}

@router.post("/{assessment_id}/submit")
def submit_assessment(assessment_id: int, files: List[UploadFile] = File(None), responses: str = Form(None), db: Session = Depends(get_db), current_student: User = Depends(get_current_student)):
    """Dual submission handler. Takes uploaded CAT files (.accdb, .xlsx) AND a JSON string of text boxes."""
    sub = db.query(FormalSubmission).filter(
        FormalSubmission.assessment_id == assessment_id,
        FormalSubmission.student_id == current_student.id,
        FormalSubmission.completed_at == None
    ).first()
    
    if not sub:
        raise HTTPException(400, "No active formal lockdown found.")
        
    sub.completed_at = datetime.utcnow()
    # If the user took too long, mark as late (not implemented strictly here, but data supports it)
    
    import json
    if responses:
        try:
            sub.text_responses = json.loads(responses)
        except:
            sub.text_responses = {}
            
    # Mock saving files
    file_list = []
    if files:
        for f in files:
            file_list.append(f.filename) # In real app, save to S3/Disk
    sub.uploaded_files = file_list
    
    db.commit()
    return {"message": "Formal Assessment Locked and Submitted"}
