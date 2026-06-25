from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, Index, DateTime, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Response(BaseModel):
    __tablename__ = "responses"
    
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    question_id = Column(String(36), ForeignKey("interview_questions.id", ondelete="CASCADE"), nullable=False, index=True)
    transcript_text = Column(Text, nullable=True)
    audio_url = Column(String(500), nullable=True)
    video_clip_url = Column(String(500), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    word_count = Column(Integer, nullable=True)
    
    # Engine Scores
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    speech_metrics = Column(JSON, nullable=True)
    feedback = Column(Text, nullable=True)
    detailed_feedback = Column(JSON, nullable=True)
    
    session = relationship("InterviewSession", foreign_keys=[session_id])
    question = relationship("InterviewQuestion", foreign_keys=[question_id])
