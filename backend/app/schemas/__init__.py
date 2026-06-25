"""
Pydantic Schemas Package

Exports all Pydantic schemas for API request/response validation.
"""

# User schemas
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserRoleUpdate,
    UserRead,
    UserInDB,
    TokenCreate,
    TokenRefresh,
    OTPRequest,
    OTPVerify,
    PasswordReset,
    AuthResponse,
    MessageResponse,
)

# Resource schemas
from app.schemas.resource import (
    ResourceBase,
    ResourceCreate,
    ResourceUpdate,
    ResourceRead,
    ResourceSummary,
    ProgressBase,
    ProgressCreate,
    ProgressUpdate,
    ProgressRead,
    ProgressWithResource,
)

# Interview schemas
from app.schemas.interview import (
    SessionBase,
    SessionCreate,
    SessionUpdate,
    SessionRead,
    SessionSummary,
    QuestionResponse,
    AddQuestionRequest,
    AddResponseRequest,
    AnalysisBase,
    AnalysisCreate,
    AnalysisUpdate,
    AnalysisRead,
    AnalysisSummary,
    AnalysisJobStart,
    AnalysisJobStatus,
)

__all__ = [
    # User
    "UserBase",
    "UserCreate",
    "UserUpdate",
    "UserRoleUpdate",
    "UserRead",
    "UserInDB",
    "TokenCreate",
    "TokenRefresh",
    "OTPRequest",
    "OTPVerify",
    "PasswordReset",
    "AuthResponse",
    "MessageResponse",
    # Resource
    "ResourceBase",
    "ResourceCreate",
    "ResourceUpdate",
    "ResourceRead",
    "ResourceSummary",
    "ProgressBase",
    "ProgressCreate",
    "ProgressUpdate",
    "ProgressRead",
    "ProgressWithResource",
    # Interview
    "SessionBase",
    "SessionCreate",
    "SessionUpdate",
    "SessionRead",
    "SessionSummary",
    "QuestionResponse",
    "AddQuestionRequest",
    "AddResponseRequest",
    "AnalysisBase",
    "AnalysisCreate",
    "AnalysisUpdate",
    "AnalysisRead",
    "AnalysisSummary",
    "AnalysisJobStart",
    "AnalysisJobStatus",
]
