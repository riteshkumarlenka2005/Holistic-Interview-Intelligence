from sqlalchemy import Column, String, Float, Integer, ForeignKey, Index, JSON, Date
from app.models.base import BaseModel

class AnalyticsSnapshot(BaseModel):
    __tablename__ = "analytics_snapshots"
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    snapshot_date = Column(Date, nullable=False)
    session_count = Column(Integer, default=0)
    avg_overall_score = Column(Float, nullable=True)
    avg_technical_score = Column(Float, nullable=True)
    avg_communication_score = Column(Float, nullable=True)
    avg_confidence_score = Column(Float, nullable=True)
    avg_eye_contact_pct = Column(Float, nullable=True)
    domain_scores = Column(JSON, default=dict)
    improvement_delta = Column(Float, nullable=True)
