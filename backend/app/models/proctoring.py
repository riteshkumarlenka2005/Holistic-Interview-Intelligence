from sqlalchemy import Column, String, Text, Float, Integer, ForeignKey, Index, JSON, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class ProctoringAlert(BaseModel):
    __tablename__ = "proctoring_alerts"
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    alert_type = Column(String(50), nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=True)
    evidence = Column(JSON, default=dict)
    timestamp_ms = Column(Integer, nullable=False)
    resolved = Column(Boolean, default=False)
    
class ProctoringSession(BaseModel):
    __tablename__ = "proctoring_sessions"
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, unique=True)
    risk_score = Column(Float, default=0.0)
    total_alerts = Column(Integer, default=0)
    critical_alerts = Column(Integer, default=0)
    proctoring_mode = Column(String(20), default="moderate")
    tab_switches = Column(Integer, default=0)
    gaze_off_duration_ms = Column(Integer, default=0)
    multi_face_events = Column(Integer, default=0)
    verdict = Column(String(20), nullable=True)
