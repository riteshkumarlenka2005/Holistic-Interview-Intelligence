from sqlalchemy import Column, String, Text, Boolean, JSON, DateTime, ForeignKey, Index, Integer, Float
from sqlalchemy.orm import relationship
try:
    from pgvector.sqlalchemy import Vector
except ImportError:
    Vector = None  # fallback for SQLite

from app.models.base import BaseModel

class Question(BaseModel):
    __tablename__ = "questions"
    
    domain = Column(String(50), nullable=True)
    difficulty = Column(String(20), nullable=True)
    question_type = Column(String(30), nullable=True)
    text = Column(Text, nullable=False)
    follow_up_prompts = Column(JSON, default=list)
    ideal_answer_outline = Column(Text, nullable=True)
    tags = Column(JSON, default=list)
    if Vector:
        embedding_vector = Column(Vector(1536), nullable=True)
    is_active = Column(Boolean, default=True)

class InterviewQuestion(BaseModel):
    __tablename__ = "interview_questions"
    
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("questions.id", ondelete="SET NULL"), nullable=True)
    question_text = Column(Text, nullable=True)
    asked_at = Column(DateTime(timezone=True), nullable=True)
    answered_at = Column(DateTime(timezone=True), nullable=True)
    answer_duration_seconds = Column(Integer, nullable=True)
    order_index = Column(Integer, nullable=False, default=0)
    was_follow_up = Column(Boolean, default=False)
    parent_question_id = Column(String(36), ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=True)
    
    session = relationship("InterviewSession", foreign_keys=[session_id])
    question = relationship("Question")
    parent = relationship("InterviewQuestion", remote_side="[InterviewQuestion.id]")
