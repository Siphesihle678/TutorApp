from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class AnnouncementBase(BaseModel):
    title: str
    content: str
    is_important: bool = False

class AnnouncementCreate(AnnouncementBase):
    pass

class AnnouncementRead(AnnouncementBase):
    id: int
    creator_id: int
    email_sent: bool
    created_at: datetime
    
    class Config:
        from_attributes = True
