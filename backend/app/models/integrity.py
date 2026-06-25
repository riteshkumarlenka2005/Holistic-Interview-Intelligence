from sqlalchemy import Column, String, Integer, ForeignKey, Index, DateTime
from app.models.base import BaseModel
from datetime import datetime, timezone

class IntegrityEvent(BaseModel):
    __tablename__ = "integrity_events"
    
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Event types: "tab_switch", "window_blur", "distraction_event", "multiple_faces"
    event_type = Column(String(50), nullable=False)
    
    # Timestamp of when the event occurred in the interview (either absolute or relative ms)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False)
    timestamp_ms = Column(Integer, nullable=True) # relative ms from start of session
    
    # Optional metadata (e.g., duration of distraction)
    details = Column(String(255), nullable=True)
