from sqlalchemy import Column, String, ForeignKey, Index, JSON, DateTime
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
