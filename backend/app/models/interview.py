"""
Interview session and analysis models.
Designed to accept AI model outputs without schema changes.
"""
import enum
from sqlalchemy import Column, String, Text, Integer, DateTime, ForeignKey, Index, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class SessionType(str, enum.Enum):
    """Types of interview sessions"""
    HR = "HR"
    TECHNICAL = "Technical"
    BEHAVIORAL = "Behavioral"
    MOCK = "Mock"
    CASE_STUDY = "Case Study"
    SITUATIONAL = "Situational"


class SessionStatus(str, enum.Enum):
    """Interview session status"""
    DRAFT = "draft"
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ANALYZED = "analyzed"
    ARCHIVED = "archived"


class InterviewTemplate(BaseModel):
    """
    Template for configuring interview sessions dynamically.
    Stores scoring weights and difficulty.
    """
    __tablename__ = "interview_templates"
    
    title = Column(String(255), nullable=False)
    target_job_role = Column(String(255), nullable=True)
    
    # Scoring Weights
    technical_weight = Column(Integer, default=70, nullable=False)
    communication_weight = Column(Integer, default=20, nullable=False)
    speech_weight = Column(Integer, default=10, nullable=False)
    confidence_weight = Column(Integer, default=0, nullable=False)
    
    # Base configuration
    base_difficulty = Column(String(50), default="intermediate", nullable=False)



class InterviewState(str, enum.Enum):
    """Real-time state machine for an active interview"""
    WAITING = "waiting"
    QUESTION_ASKED = "question_asked"
    ANSWERING = "answering"
    EVALUATING = "evaluating"
    FOLLOW_UP = "follow_up"
    NEXT_QUESTION = "next_question"
    COMPLETED = "completed"


class InterviewSession(BaseModel):
    """
    Interview session model.
    
    Tracks the lifecycle of an interview from creation to completion.
    Stores questions and responses for later analysis.
    """
    __tablename__ = "interview_sessions"
    
    # Foreign keys
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Session details
    title = Column(String(255), nullable=True)
    session_type = Column(String(50), default=SessionType.MOCK.value, nullable=False)
    status = Column(String(20), default=SessionStatus.DRAFT.value, nullable=False)
    current_state = Column(String(20), default=InterviewState.WAITING.value, nullable=False)
    
    # Target information
    target_job_role = Column(String(255), nullable=True)
    target_company = Column(String(255), nullable=True)
    
    # Duration
    duration_minutes = Column(Integer, default=30, nullable=False)
    difficulty_modifier = Column(Integer, default=0, nullable=False)
    
    # Session timing
    started_at = Column(DateTime(timezone=True), nullable=True)
    ended_at = Column(DateTime(timezone=True), nullable=True)
    
    # Questions and responses stored as JSON for flexibility
    questions = Column(JSON, default=list, nullable=False)
    responses = Column(JSON, default=list, nullable=False)
    
    # Notes
    notes = Column(Text, nullable=True)
    
    # Topic Memory — prevents repetitive question generation
    # Schema: [{"topic": str, "subtopic": str, "difficulty": str, "question_text": str}]
    asked_topics = Column(JSON, default=list, nullable=False)
    
    # Media references
    video_url = Column(String(500), nullable=True)
    audio_url = Column(String(500), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="interview_sessions")
    analysis = relationship("InterviewAnalysis", back_populates="session", uselist=False, cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("ix_interview_sessions_user_status", "user_id", "status"),
        Index("ix_interview_sessions_type", "session_type"),
        Index("ix_interview_sessions_started", "started_at"),
    )
    
    @property
    def actual_duration_minutes(self) -> int | None:
        """Calculate actual duration if session has ended"""
        if self.started_at and self.ended_at:
            delta = self.ended_at - self.started_at
            return int(delta.total_seconds() / 60)
        return None
    
    @property
    def is_complete(self) -> bool:
        """Check if session is completed or analyzed"""
        return self.status in [SessionStatus.COMPLETED.value, SessionStatus.ANALYZED.value]
    
    def __repr__(self):
        return f"<InterviewSession {self.id} ({self.session_type})>"


class InterviewAnalysis(BaseModel):
    """
    AI analysis results for interview sessions.
    
    Uses JSON fields for flexible storage of ML model outputs.
    This design allows new AI signals to be added without schema changes.
    
    JSON Fields Structure (examples):
    
    verbal_metrics:
    {
        "transcription": {"text": "...", "segments": [...]},
        "prosody": {"pace": {"wpm": 140, "assessment": "normal"}, "volume": {...}},
        "fillers": {"filler_rate_per_minute": 3.5, "fillers": ["um", "uh"]},
        "confidence": {"overall_score": 0.72, "segments": [...]}
    }
    
    nonverbal_metrics:
    {
        "gaze": {"eye_contact_percentage": 68, "looking_away_moments": [...]},
        "posture": {"dominant_posture": "upright", "engagement_score": 0.75},
        "expressions": {"dominant_expression": "neutral", "timeline": [...]}
    }
    
    multimodal_score:
    {
        "combined_confidence": 0.70,
        "communication_score": 0.72,
        "presence_score": 0.75,
        "engagement_score": 0.68,
        "authenticity_score": 0.80,
        "congruence": {"verbal_nonverbal_alignment": 0.85}
    }
    
    recommendations:
    {
        "overall_assessment": {"overall_score": 72, "grade": "B", "label": "Good"},
        "strengths": ["Clear communication", "Good eye contact"],
        "improvements": ["Reduce filler words", "Speak more slowly"],
        "actionable_tips": ["Practice STAR method", "Use pauses effectively"],
        "llm_feedback": {"summary": "...", "detailed_feedback": "..."}
    }
    """
    __tablename__ = "interview_analysis"
    
    # Foreign key to session
    session_id = Column(String(36), ForeignKey("interview_sessions.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # AI analysis outputs - all stored as JSON for flexibility
    verbal_metrics = Column(JSON, default=dict, nullable=False)
    nonverbal_metrics = Column(JSON, default=dict, nullable=False)
    multimodal_score = Column(JSON, default=dict, nullable=False)
    recommendations = Column(JSON, default=dict, nullable=False)
    
    # Processing metadata
    analysis_version = Column(String(20), default="1.0", nullable=False)
    processing_time_seconds = Column(Integer, nullable=True)
    
    # Explainability outputs (for XAI features)
    explainability = Column(JSON, default=dict, nullable=True)
    
    # Relationships
    session = relationship("InterviewSession", back_populates="analysis")
    
    def __repr__(self):
        return f"<InterviewAnalysis session={self.session_id}>"
    
    @property
    def overall_score(self) -> float | None:
        """Get overall score from multimodal analysis"""
        if self.multimodal_score:
            return self.multimodal_score.get("combined_confidence")
        return None
    
    @property
    def has_verbal_analysis(self) -> bool:
        """Check if verbal analysis is available"""
        return bool(self.verbal_metrics)
    
    @property
    def has_nonverbal_analysis(self) -> bool:
        """Check if nonverbal analysis is available"""
        return bool(self.nonverbal_metrics)
