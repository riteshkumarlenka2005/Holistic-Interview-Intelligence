from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, JSON, ForeignKey, Float
from sqlalchemy.orm import relationship
from app.db.base_class import Base

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(String, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"))
    job_role = Column(String, nullable=True)
    target_job_role = Column(String, nullable=True) # Legacy mapping
    
    # State tracking
    current_state = Column(String, default="WAITING")
    status = Column(String, default="pending")
    difficulty_modifier = Column(Integer, default=0)
    
    # Context & Timeline
    asked_topics = Column(JSON, default=list) # Memory of topics asked
    interview_timeline = Column(JSON, default=list) # Unified Phase 6 Timeline
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    # Relationships
    user = relationship("User", back_populates="sessions")
    questions = relationship("InterviewQuestion", back_populates="session", cascade="all, delete-orphan")
    responses = relationship("Response", back_populates="session", cascade="all, delete-orphan")
