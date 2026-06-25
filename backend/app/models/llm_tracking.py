from sqlalchemy import Column, String, Float, Integer, ForeignKey, Index
from app.models.base import BaseModel

class LLMRequest(BaseModel):
    """
    Tracks LLM usage per session for cost estimation and prompt optimization.
    """
    __tablename__ = "llm_requests"
    
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=True, index=True)
    model = Column(String(100), nullable=False)
    purpose = Column(String(50), nullable=True, index=True) # e.g. 'question_gen', 'coaching', 'report'
    
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    estimated_cost = Column(Float, default=0.0) # In USD
    latency_ms = Column(Integer, default=0)
    
    __table_args__ = (
        Index("ix_llm_requests_model", "model"),
    )
