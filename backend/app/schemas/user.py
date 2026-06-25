"""
User-related Pydantic schemas for API request/response validation.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator
import re


# ============= User Schemas =============

class UserBase(BaseModel):
    """Base user schema with common fields"""
    email: EmailStr
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)


class UserCreate(UserBase):
    """Schema for user registration"""
    password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v


class UserUpdate(BaseModel):
    """Schema for updating user profile"""
    first_name: Optional[str] = Field(None, max_length=100)
    last_name: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = Field(None, max_length=500)


class UserRoleUpdate(BaseModel):
    """Schema for updating user role (admin only)"""
    role: str = Field(..., pattern='^(student|admin|coach)$')


class UserRead(UserBase):
    """Schema for reading user data (public)"""
    id: str
    avatar_url: Optional[str] = None
    role: str
    is_verified: bool
    is_active: bool
    oauth_provider: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserInDB(UserRead):
    """Schema for internal user data (includes sensitive info)"""
    password_hash: Optional[str] = None
    oauth_id: Optional[str] = None
    last_login: Optional[datetime] = None
    updated_at: datetime
    
    class Config:
        from_attributes = True


# ============= Token Schemas =============

class TokenCreate(BaseModel):
    """Schema for creating authentication tokens"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes in seconds


class TokenRefresh(BaseModel):
    """Schema for refresh token request"""
    refresh_token: str


# ============= OTP Schemas =============

class OTPRequest(BaseModel):
    """Schema for OTP-related requests"""
    email: EmailStr


class OTPVerify(BaseModel):
    """Schema for OTP verification"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)


class PasswordReset(BaseModel):
    """Schema for password reset"""
    email: EmailStr
    code: str = Field(..., min_length=6, max_length=6)
    new_password: str = Field(..., min_length=8, max_length=128)
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


# ============= Auth Response Schemas =============

class AuthResponse(BaseModel):
    """Response schema for authentication endpoints"""
    user: UserRead
    tokens: TokenCreate


class MessageResponse(BaseModel):
    """Generic message response"""
    message: str
    success: bool = True
