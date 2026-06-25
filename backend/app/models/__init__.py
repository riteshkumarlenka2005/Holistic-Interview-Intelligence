"""
Database Models Package

Exports all SQLAlchemy models for the application.
Import models from this package for use in the application.
"""

# Base model and mixins
from app.models.base import Base, BaseModel, UUIDMixin, TimestampMixin

# User models
from app.models.user import (
    User,
    OTPToken,
    RefreshToken,
    UserRole,
    OAuthProvider,
    OTPType,
)

# Resource models
from app.models.resource import (
    LearningResource,
    ResourceProgress,
    ResourceType,
    DifficultyLevel,
)

# Interview models
from app.models.interview import (
    InterviewSession,
    InterviewAnalysis,
    SessionType,
    SessionStatus,
    InterviewTemplate,
)

# AI Interview Models
from app.models.questions import Question, InterviewQuestion
from app.models.responses import Response
from app.models.transcripts import Transcript
from app.models.analysis_results import (
    SpeechMetrics, FaceMetrics, EyeTrackingData, EmotionTimeline,
    ConfidenceTimeline, TechnicalScore, CommunicationScore
)
from app.models.proctoring import ProctoringAlert, ProctoringSession
from app.models.coaching import CoachingEvent
from app.models.reports import Report
from app.models.analytics import AnalyticsSnapshot
from app.models.jobs import AnalysisJob
from app.models.integrity import IntegrityEvent
from app.models.llm_tracking import LLMRequest

__all__ = [
    # Base
    "Base", "BaseModel", "UUIDMixin", "TimestampMixin",
    # User
    "User", "OTPToken", "RefreshToken", "UserRole", "OAuthProvider", "OTPType",
    # Resource
    "LearningResource", "ResourceProgress", "ResourceType", "DifficultyLevel",
    # Interview
    "InterviewSession", "InterviewAnalysis", "SessionType", "SessionStatus", "InterviewTemplate",
    # New AI Platform
    "Question", "InterviewQuestion", "Response", "Transcript",
    "SpeechMetrics", "FaceMetrics", "EyeTrackingData", "EmotionTimeline",
    "ConfidenceTimeline", "TechnicalScore", "CommunicationScore",
    "ProctoringAlert", "ProctoringSession", "CoachingEvent",
    "Report", "AnalyticsSnapshot", "AnalysisJob", "IntegrityEvent", "LLMRequest"
]
