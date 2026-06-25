from sqlalchemy import Column, String, Text, Integer, ForeignKey, Index, JSON, Boolean, DateTime
from app.models.base import BaseModel

class CoachingEvent(BaseModel):
    __tablename__ = "coaching_events"
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    timestamp_ms = Column(Integer, nullable=False, index=True)
    trigger_type = Column(String(50), nullable=False)
    trigger_metric = Column(JSON, default=dict)
    message = Column(Text, nullable=False)
    severity = Column(String(20), nullable=False)
    category = Column(String(30), nullable=False)
    acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
