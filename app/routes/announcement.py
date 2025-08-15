from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from ..core.database import get_db
from ..core.auth import get_current_teacher, get_current_user
from ..models.user import User
from ..models.announcement import Announcement
from ..schemas.announcement import AnnouncementCreate, AnnouncementRead
from ..services.email_service import email_service

router = APIRouter()

# ==================== PUBLIC ENDPOINTS ====================

@router.get("/public", response_model=List[AnnouncementRead])
def get_public_announcements(db: Session = Depends(get_db)):
    """Get public announcement list (no authentication required)"""
    announcements = db.query(Announcement).order_by(Announcement.created_at.desc()).all()
    return announcements

@router.get("/public/{announcement_id}")
def get_public_announcement(announcement_id: int, db: Session = Depends(get_db)):
    """Get public announcement details (no authentication required)"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    
    return {
        "id": announcement.id,
        "title": announcement.title,
        "content": announcement.content,
        "is_important": announcement.is_important,
        "created_at": announcement.created_at
    }

# ==================== PROTECTED ENDPOINTS ====================

@router.post("/", response_model=AnnouncementRead)
def create_announcement(
    announcement_data: AnnouncementCreate,
    current_teacher: User = Depends(get_current_teacher),
    db: Session = Depends(get_db)
):
    """Create a new announcement (teachers only)"""
    db_announcement = Announcement(
        title=announcement_data.title,
        content=announcement_data.content,
        is_important=announcement_data.is_important,
        creator_id=current_teacher.id
    )
    
    db.add(db_announcement)
    db.commit()
    db.refresh(db_announcement)
    
    # Send email notifications to all students
    if announcement_data.is_important:
        students = db.query(User).filter(User.role == "student", User.is_active == True).all()
        student_emails = [student.email for student in students]
        
        if student_emails:
            email_service.send_announcement_notification(
                student_emails,
                announcement_data.title,
                announcement_data.content
            )
            db_announcement.email_sent = True
            db.commit()
    
    return db_announcement

@router.get("/", response_model=List[AnnouncementRead])
def list_announcements(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all announcements"""
    announcements = db.query(Announcement).order_by(Announcement.created_at.desc()).all()
    return announcements

@router.get("/{announcement_id}", response_model=AnnouncementRead)
def get_announcement(
    announcement_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get announcement details"""
    announcement = db.query(Announcement).filter(Announcement.id == announcement_id).first()
    if not announcement:
        raise HTTPException(status_code=404, detail="Announcement not found")
    return announcement
