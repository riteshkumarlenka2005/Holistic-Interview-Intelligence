from sqlalchemy import Column, String, Text, JSON, ForeignKey, Index
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Transcript(BaseModel):
    __tablename__ = "transcripts"
    
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    response_id = Column(String(36), ForeignKey("responses.id", ondelete="CASCADE"), nullable=True)
    full_text = Column(Text, nullable=True)
    word_timestamps = Column(JSON, default=list)
    segments = Column(JSON, default=list)
    language = Column(String(10), default="en")
    model_used = Column(String(50), nullable=True)
