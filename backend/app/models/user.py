"""
User-related database models.
Includes User, OTPToken, and RefreshToken models.
"""
import enum
from datetime import datetime
import uuid

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.models.base import BaseModel


class UserRole(str, enum.Enum):
    """User roles for access control"""
    CANDIDATE = "candidate"
    ADMIN = "admin"
    RECRUITER = "recruiter"


class OAuthProvider(str, enum.Enum):
    """OAuth provider types"""
    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"


class OTPType(str, enum.Enum):
    """OTP token types"""
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


class User(BaseModel):
    """
    User model for authentication and profile.
    
    Supports local authentication and OAuth providers (Google, GitHub).
    Includes role-based access control for students, admins, and coaches.
    """
    __tablename__ = "users"
    
    # Profile
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Role and status
    role = Column(String(20), default=UserRole.CANDIDATE.value, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # OAuth
    oauth_provider = Column(String(20), default=OAuthProvider.LOCAL.value)
    oauth_id = Column(String(255), nullable=True)
    
    # Activity tracking
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    otp_tokens = relationship("OTPToken", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    resource_progress = relationship("ResourceProgress", back_populates="user", cascade="all, delete-orphan")
    interview_sessions = relationship("InterviewSession", back_populates="user", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("ix_users_role", "role"),
        Index("ix_users_oauth", "oauth_provider", "oauth_id"),
    )
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or self.email.split("@")[0]
    
    @property
    def is_admin(self) -> bool:
        """Check if user has admin role"""
        return self.role == UserRole.ADMIN.value
    
    @property
    def is_recruiter(self) -> bool:
        """Check if user has recruiter role"""
        return self.role == UserRole.RECRUITER.value
    
    def __repr__(self):
        return f"<User {self.email}>"


class OTPToken(BaseModel):
    """
    OTP tokens for email verification and password reset.
    Tokens are single-use and time-limited.
    """
    __tablename__ = "otp_tokens"
    
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    code = Column(String(6), nullable=False)
    otp_type = Column(String(30), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="otp_tokens")
    
    @property
    def is_expired(self) -> bool:
        """Check if OTP has expired"""
        now = datetime.now(tz=self.expires_at.tzinfo) if self.expires_at.tzinfo else datetime.utcnow()
        return now > self.expires_at.replace(tzinfo=None) if not self.expires_at.tzinfo else now > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if OTP is still valid (not used and not expired)"""
        return not self.used and not self.is_expired


class RefreshToken(BaseModel):
    """
    Refresh tokens for JWT authentication.
    Supports token rotation and revocation.
    """
    __tablename__ = "refresh_tokens"
    
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)
    
    # Session info
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    @property
    def is_valid(self) -> bool:
        """Check if refresh token is still valid"""
        now = datetime.now(tz=self.expires_at.tzinfo) if self.expires_at.tzinfo else datetime.utcnow()
        if self.expires_at.tzinfo:
            return not self.revoked and now < self.expires_at
        return not self.revoked and datetime.utcnow() < self.expires_at.replace(tzinfo=None)
