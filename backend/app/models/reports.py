from sqlalchemy import Column, String, ForeignKey, Index, JSON, DateTime, Float, Integer
from app.models.base import BaseModel

class Report(BaseModel):
    __tablename__ = "reports"
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    report_type = Column(String(20), default="full")
    status = Column(String(20), default="generating")
    data = Column(JSON, default=dict)
    pdf_url = Column(String(500), nullable=True)
    share_token = Column(String(64), nullable=True, unique=True, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Aggregated metrics for benchmarking
    overall_score = Column(Float, nullable=True, index=True)
    technical_score = Column(Float, nullable=True)
    communication_score = Column(Float, nullable=True)
    integrity_score = Column(Float, nullable=True)
    difficulty_level = Column(String(50), nullable=True)
    
    # Model Versioning tracking
    engine = Column(String(100), nullable=True)
    prompt_version = Column(String(50), nullable=True)
    generated_at = Column(DateTime(timezone=True), nullable=True)
