from sqlalchemy import Column, String, Integer, ForeignKey, Index, JSON, DateTime, Text
from app.models.base import BaseModel

class AnalysisJob(BaseModel):
    __tablename__ = "analysis_jobs"
    celery_task_id = Column(String(255), nullable=True, index=True)
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    job_type = Column(String(50), nullable=False)
    status = Column(String(20), default="pending", index=True)
    progress = Column(Integer, default=0)
    current_step = Column(String(100), nullable=True)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
