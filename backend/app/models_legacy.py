"""
Database models for authentication
"""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text, Integer, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime, timedelta
import uuid
import enum

from app.core.database import Base


class OAuthProvider(str, enum.Enum):
    LOCAL = "local"
    GOOGLE = "google"
    GITHUB = "github"


class OTPType(str, enum.Enum):
    EMAIL_VERIFICATION = "email_verification"
    PASSWORD_RESET = "password_reset"


class User(Base):
    """User model for authentication"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True)  # Nullable for OAuth users
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    avatar_url = Column(String(500), nullable=True)
    
    # Email verification
    is_verified = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # OAuth provider info
    oauth_provider = Column(String(20), default=OAuthProvider.LOCAL.value)
    oauth_id = Column(String(255), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    otp_tokens = relationship("OTPToken", back_populates="user", cascade="all, delete-orphan")
    refresh_tokens = relationship("RefreshToken", back_populates="user", cascade="all, delete-orphan")
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        parts = [self.first_name, self.last_name]
        return " ".join(p for p in parts if p) or self.email.split("@")[0]
    
    def __repr__(self):
        return f"<User {self.email}>"


class OTPToken(Base):
    """OTP tokens for email verification and password reset"""
    __tablename__ = "otp_tokens"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    code = Column(String(6), nullable=False)
    otp_type = Column(String(20), nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    used = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    user = relationship("User", back_populates="otp_tokens")
    
    @property
    def is_expired(self) -> bool:
        """Check if OTP has expired"""
        return datetime.utcnow() > self.expires_at.replace(tzinfo=None)
    
    @property
    def is_valid(self) -> bool:
        """Check if OTP is still valid (not used and not expired)"""
        return not self.used and not self.is_expired


class RefreshToken(Base):
    """Refresh tokens for JWT authentication"""
    __tablename__ = "refresh_tokens"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(500), unique=True, nullable=False, index=True)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    revoked = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Device/session info (optional)
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="refresh_tokens")
    
    @property
    def is_valid(self) -> bool:
        """Check if refresh token is still valid"""
        return not self.revoked and datetime.utcnow() < self.expires_at.replace(tzinfo=None)
