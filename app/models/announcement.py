from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..core.database import Base

class Announcement(Base):
    __tablename__ = "announcements"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    is_important = Column(Boolean, default=False)
    email_sent = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Foreign Keys
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    creator = relationship("User", back_populates="announcements_created")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(Integer, primary_key=True, index=True)
    recipient_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    is_read = Column(Boolean, default=False)
    type = Column(String, default="reminder") # info, reminder, alert
    link_url = Column(String, nullable=True)  # Optional deep link
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship
    recipient = relationship("User", foreign_keys=[recipient_id])
