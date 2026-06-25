"""
Interview session and analysis Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


# ============= Interview Session Schemas =============

class SessionBase(BaseModel):
    """Base session schema"""
    title: Optional[str] = Field(None, max_length=255)
    session_type: str = Field(default="Mock", pattern='^(HR|Technical|Behavioral|Mock|Case Study|Situational)$')
    target_job_role: Optional[str] = Field(None, max_length=255)
    target_company: Optional[str] = Field(None, max_length=255)
    duration_minutes: int = Field(default=30, ge=5, le=180)


class SessionCreate(SessionBase):
    """Schema for creating an interview session"""
    questions: List[str] = Field(default_factory=list)
    notes: Optional[str] = None


class SessionUpdate(BaseModel):
    """Schema for updating an interview session"""
    title: Optional[str] = Field(None, max_length=255)
    session_type: Optional[str] = Field(None, pattern='^(HR|Technical|Behavioral|Mock|Case Study|Situational)$')
    status: Optional[str] = Field(None, pattern='^(draft|scheduled|in_progress|completed|analyzed|archived)$')
    target_job_role: Optional[str] = Field(None, max_length=255)
    target_company: Optional[str] = Field(None, max_length=255)
    duration_minutes: Optional[int] = Field(None, ge=5, le=180)
    questions: Optional[List[str]] = None
    notes: Optional[str] = None


class SessionRead(SessionBase):
    """Schema for reading an interview session"""
    id: str
    user_id: str
    status: str
    questions: List[str]
    responses: List[Dict[str, Any]]
    notes: Optional[str] = None
    video_url: Optional[str] = None
    audio_url: Optional[str] = None
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SessionSummary(BaseModel):
    """Summary schema for listing sessions"""
    id: str
    title: Optional[str] = None
    session_type: str
    status: str
    target_job_role: Optional[str] = None
    created_at: datetime
    
    class Config:
        from_attributes = True


class QuestionResponse(BaseModel):
    """Schema for a question response"""
    question_index: int
    question_text: str
    response_text: Optional[str] = None
    response_duration_seconds: Optional[float] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None


class AddQuestionRequest(BaseModel):
    """Schema for adding a question"""
    question: str = Field(..., min_length=1)


class AddResponseRequest(BaseModel):
    """Schema for adding a response"""
    question_index: int = Field(..., ge=0)
    response_text: Optional[str] = None
    audio_url: Optional[str] = None
    video_url: Optional[str] = None
    duration_seconds: Optional[float] = None


# ============= Interview Analysis Schemas =============

class IntegrityEventCreate(BaseModel):
    event_type: str = Field(..., pattern='^(tab_switch|window_blur|distraction_event|multiple_faces)$')
    timestamp_ms: Optional[int] = None
    details: Optional[str] = None

class IntegrityEventRead(IntegrityEventCreate):
    id: str
    session_id: str
    timestamp: datetime
    
    class Config:
        from_attributes = True

# ============= Interview Analysis Schemas =============

class AnalysisBase(BaseModel):
    """Base analysis schema"""
    verbal_metrics: Dict[str, Any] = Field(default_factory=dict)
    nonverbal_metrics: Dict[str, Any] = Field(default_factory=dict)
    multimodal_score: Dict[str, Any] = Field(default_factory=dict)
    recommendations: Dict[str, Any] = Field(default_factory=dict)


class AnalysisCreate(AnalysisBase):
    """Schema for creating analysis record"""
    session_id: str
    analysis_version: str = "1.0"
    processing_time_seconds: Optional[int] = None
    explainability: Optional[Dict[str, Any]] = None


class AnalysisUpdate(BaseModel):
    """Schema for updating analysis"""
    verbal_metrics: Optional[Dict[str, Any]] = None
    nonverbal_metrics: Optional[Dict[str, Any]] = None
    multimodal_score: Optional[Dict[str, Any]] = None
    recommendations: Optional[Dict[str, Any]] = None
    explainability: Optional[Dict[str, Any]] = None


class AnalysisRead(AnalysisBase):
    """Schema for reading analysis"""
    id: str
    session_id: str
    analysis_version: str
    processing_time_seconds: Optional[int] = None
    explainability: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class AnalysisSummary(BaseModel):
    """Summary of analysis results"""
    overall_score: Optional[float] = None
    communication_score: Optional[float] = None
    presence_score: Optional[float] = None
    engagement_score: Optional[float] = None
    top_recommendations: List[str] = Field(default_factory=list)


# ============= Analysis Job Schemas =============

class AnalysisJobStart(BaseModel):
    """Schema for starting an analysis job"""
    session_id: str
    analysis_type: str = Field(default="multimodal", pattern='^(speech|vision|multimodal)$')
    include_transcription: bool = True
    include_prosody: bool = True
    include_gaze: bool = True
    include_posture: bool = True
    include_expressions: bool = True
    enable_llm_feedback: bool = False


class AnalysisJobStatus(BaseModel):
    """Schema for analysis job status"""
    job_id: str
    session_id: str
    status: str
    progress: float = Field(ge=0, le=100)
    current_step: Optional[str] = None
    message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None


# ============= Analysis API Schemas (used by analysis.py router) =============

from enum import Enum as PyEnum

class AnalysisType(str, PyEnum):
    SPEECH = "speech"
    VISION = "vision"
    MULTIMODAL = "multimodal"

class AnalysisStatus(str, PyEnum):
    PENDING = "pending"
    STARTED = "started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class AnalysisConfig(BaseModel):
    analysis_type: AnalysisType = AnalysisType.MULTIMODAL
    interview_question: Optional[str] = None
    target_job_role: Optional[str] = None
    include_transcription: bool = True
    include_gaze: bool = True
    enable_llm_feedback: bool = True

class AnalysisStartRequest(BaseModel):
    interview_id: str
    config: Optional[AnalysisConfig] = None

class AnalysisStatusResponse(BaseModel):
    interview_id: str
    job_id: str
    status: AnalysisStatus
    progress: float = 0.0
    current_step: Optional[str] = None
    message: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None

