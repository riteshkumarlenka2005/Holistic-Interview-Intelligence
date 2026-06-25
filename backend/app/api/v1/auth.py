"""
Authentication API endpoints
Complete implementation with email OTP, Google OAuth, and GitHub OAuth
"""
from fastapi import APIRouter, HTTPException, Depends, Request, Response
from fastapi.responses import RedirectResponse
from pydantic import BaseModel, EmailStr, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from typing import Optional
import re

from app.core.config import get_settings
from app.core.database import get_db
from app.core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    get_current_user
)
from app.models import User, OTPToken, RefreshToken, OTPType, OAuthProvider
from app.services import (
    send_verification_email,
    send_password_reset_email,
    create_otp_token,
    verify_otp,
    resend_otp,
    GoogleOAuth,
    GitHubOAuth
)

router = APIRouter()
settings = get_settings()


# ============ Request/Response Models ============

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'\d', v):
            raise ValueError('Password must contain at least one number')
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class VerifyOTPRequest(BaseModel):
    email: EmailStr
    code: str


class ResendOTPRequest(BaseModel):
    email: EmailStr


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    code: str
    new_password: str
    
    @field_validator('new_password')
    @classmethod
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters')
        return v


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int = 1800  # 30 minutes in seconds


class UserResponse(BaseModel):
    id: str
    email: str
    first_name: Optional[str]
    last_name: Optional[str]
    avatar_url: Optional[str]
    is_verified: bool
    oauth_provider: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class AuthResponse(BaseModel):
    user: UserResponse
    tokens: TokenResponse


class MessageResponse(BaseModel):
    message: str
    success: bool = True


# ============ Helper Functions ============

async def create_tokens_for_user(
    db: AsyncSession, 
    user: User,
    request: Request = None
) -> TokenResponse:
    """Create access and refresh tokens for a user"""
    # Create access token
    access_token = create_access_token(data={"sub": user.id})
    
    # Create refresh token
    token_value, expires_at = create_refresh_token()
    
    refresh_token = RefreshToken(
        user_id=user.id,
        token=token_value,
        expires_at=expires_at,
        user_agent=request.headers.get("user-agent") if request else None,
        ip_address=request.client.host if request and request.client else None
    )
    db.add(refresh_token)
    
    # Update last login
    user.last_login = datetime.utcnow()
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=token_value,
        expires_in=settings.access_token_expire_minutes * 60
    )


# ============ Email Authentication ============

@router.post("/register", response_model=MessageResponse, status_code=201)
async def register(
    request_data: RegisterRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user with email and password.
    Sends a 6-digit OTP for email verification.
    """
    # Check if user already exists
    result = await db.execute(
        select(User).where(User.email == request_data.email)
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        if existing_user.is_verified:
            raise HTTPException(
                status_code=400,
                detail="An account with this email already exists"
            )
        else:
            # User exists but not verified - resend OTP
            otp_token = await create_otp_token(db, existing_user.id, OTPType.EMAIL_VERIFICATION)
            await send_verification_email(
                existing_user.email, 
                otp_token.code,
                existing_user.first_name
            )
            return MessageResponse(
                message="Verification code sent to your email. Please verify to complete registration."
            )
    
    # Create new user
    user = User(
        email=request_data.email,
        password_hash=get_password_hash(request_data.password),
        first_name=request_data.first_name,
        last_name=request_data.last_name,
        is_verified=False,
        oauth_provider=OAuthProvider.LOCAL.value
    )
    db.add(user)
    await db.flush()
    
    # Create OTP for email verification
    otp_token = await create_otp_token(db, user.id, OTPType.EMAIL_VERIFICATION)
    
    # Send verification email
    await send_verification_email(
        user.email,
        otp_token.code,
        user.first_name
    )
    
    return MessageResponse(
        message="Registration successful! Please check your email for the verification code."
    )


@router.post("/verify-email", response_model=AuthResponse)
async def verify_email(
    request_data: VerifyOTPRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Verify email with 6-digit OTP code.
    Returns tokens on successful verification.
    """
    success, message, user = await verify_otp(
        db, 
        request_data.email, 
        request_data.code, 
        OTPType.EMAIL_VERIFICATION
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    # Create tokens
    tokens = await create_tokens_for_user(db, user, request)
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens
    )


@router.post("/resend-otp", response_model=MessageResponse)
async def resend_verification_otp(
    request_data: ResendOTPRequest,
    db: AsyncSession = Depends(get_db)
):
    """Resend email verification OTP"""
    success, message, otp_code = await resend_otp(
        db, 
        request_data.email, 
        OTPType.EMAIL_VERIFICATION
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    # Get user for email
    result = await db.execute(
        select(User).where(User.email == request_data.email)
    )
    user = result.scalar_one_or_none()
    
    if user:
        await send_verification_email(user.email, otp_code, user.first_name)
    
    return MessageResponse(message="Verification code sent successfully")


@router.post("/login", response_model=AuthResponse)
async def login(
    request_data: LoginRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """
    Login with email and password.
    Requires email to be verified.
    """
    # Find user
    result = await db.execute(
        select(User).where(User.email == request_data.email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Check if user registered with OAuth
    if user.oauth_provider != OAuthProvider.LOCAL.value:
        raise HTTPException(
            status_code=400,
            detail=f"This account uses {user.oauth_provider} login. Please sign in with {user.oauth_provider}."
        )
    
    # Verify password
    if not user.password_hash or not verify_password(request_data.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    # Check if verified
    if not user.is_verified:
        # Send new OTP
        otp_token = await create_otp_token(db, user.id, OTPType.EMAIL_VERIFICATION)
        await send_verification_email(user.email, otp_token.code, user.first_name)
        raise HTTPException(
            status_code=403,
            detail="Email not verified. A new verification code has been sent to your email."
        )
    
    # Check if active
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is disabled. Please contact support."
        )
    
    # Create tokens
    tokens = await create_tokens_for_user(db, user, request)
    
    return AuthResponse(
        user=UserResponse.model_validate(user),
        tokens=tokens
    )


# ============ Password Reset ============

@router.post("/forgot-password", response_model=MessageResponse)
async def forgot_password(
    request_data: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Request password reset OTP"""
    result = await db.execute(
        select(User).where(User.email == request_data.email)
    )
    user = result.scalar_one_or_none()
    
    # Always return success to prevent email enumeration
    if user and user.oauth_provider == OAuthProvider.LOCAL.value:
        otp_token = await create_otp_token(db, user.id, OTPType.PASSWORD_RESET)
        await send_password_reset_email(user.email, otp_token.code, user.first_name)
    
    return MessageResponse(
        message="If an account with this email exists, you will receive a password reset code."
    )


@router.post("/reset-password", response_model=MessageResponse)
async def reset_password(
    request_data: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db)
):
    """Reset password with OTP"""
    success, message, user = await verify_otp(
        db,
        request_data.email,
        request_data.code,
        OTPType.PASSWORD_RESET
    )
    
    if not success:
        raise HTTPException(status_code=400, detail=message)
    
    # Update password
    user.password_hash = get_password_hash(request_data.new_password)
    
    # Revoke all refresh tokens for security
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.user_id == user.id)
    )
    for token in result.scalars():
        token.revoked = True
    
    return MessageResponse(message="Password reset successful. Please login with your new password.")


# ============ Token Management ============

@router.post("/refresh", response_model=TokenResponse)
async def refresh_access_token(
    request_data: RefreshTokenRequest,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Refresh access token using refresh token"""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == request_data.refresh_token)
    )
    refresh_token = result.scalar_one_or_none()
    
    if not refresh_token or not refresh_token.is_valid:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token"
        )
    
    # Get user
    result = await db.execute(
        select(User).where(User.id == refresh_token.user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=401,
            detail="User not found or disabled"
        )
    
    # Revoke old refresh token
    refresh_token.revoked = True
    
    # Create new tokens
    return await create_tokens_for_user(db, user, request)


@router.post("/logout", response_model=MessageResponse)
async def logout(
    request_data: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db)
):
    """Logout and revoke refresh token"""
    result = await db.execute(
        select(RefreshToken).where(RefreshToken.token == request_data.refresh_token)
    )
    refresh_token = result.scalar_one_or_none()
    
    if refresh_token:
        refresh_token.revoked = True
    
    return MessageResponse(message="Logged out successfully")


# ============ OAuth - Google ============

@router.get("/google/status")
async def google_auth_status():
    """Check if Google OAuth is configured"""
    return {"configured": bool(settings.google_client_id and settings.google_client_secret)}


@router.get("/google")
async def google_auth():
    """Redirect to Google OAuth consent page"""
    if not settings.google_client_id:
        return RedirectResponse(
            url=f"{settings.frontend_url}/login?error=Google+login+is+not+configured+on+this+server"
        )

    auth_url = GoogleOAuth.get_auth_url()
    return RedirectResponse(url=auth_url)


@router.get("/google/callback")
async def google_callback(
    code: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle Google OAuth callback"""
    # Exchange code for user info
    user_info = await GoogleOAuth.exchange_code(code)
    
    if not user_info or not user_info.get("email"):
        return RedirectResponse(
            url=f"{settings.frontend_url}/login?error=google_auth_failed"
        )
    
    # Find or create user
    result = await db.execute(
        select(User).where(User.email == user_info["email"])
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Update OAuth info if needed
        if user.oauth_provider == OAuthProvider.LOCAL.value:
            # User registered with email, link Google account
            user.oauth_provider = OAuthProvider.GOOGLE.value
            user.oauth_id = user_info.get("oauth_id")
        if not user.avatar_url and user_info.get("picture"):
            user.avatar_url = user_info["picture"]
        user.is_verified = True  # Google verified the email
    else:
        # Create new user
        user = User(
            email=user_info["email"],
            first_name=user_info.get("first_name"),
            last_name=user_info.get("last_name"),
            avatar_url=user_info.get("picture"),
            is_verified=True,  # Google verified the email
            oauth_provider=OAuthProvider.GOOGLE.value,
            oauth_id=user_info.get("oauth_id")
        )
        db.add(user)
        await db.flush()
    
    # Create tokens
    tokens = await create_tokens_for_user(db, user, request)
    await db.commit()
    
    # Redirect to frontend with tokens
    redirect_url = (
        f"{settings.frontend_url}/auth/callback"
        f"?access_token={tokens.access_token}"
        f"&refresh_token={tokens.refresh_token}"
        f"&provider=google"
    )
    return RedirectResponse(url=redirect_url)


# ============ OAuth - GitHub ============

@router.get("/github")
async def github_auth():
    """Redirect to GitHub OAuth consent page"""
    if not settings.github_client_id:
        return RedirectResponse(
            url=f"{settings.frontend_url}/login?error=GitHub+login+is+not+configured+on+this+server"
        )

    auth_url = GitHubOAuth.get_auth_url()
    return RedirectResponse(url=auth_url)


@router.get("/github/status")
async def github_auth_status():
    """Check if GitHub OAuth is configured"""
    return {"configured": bool(settings.github_client_id and settings.github_client_secret)}


@router.get("/github/callback")
async def github_callback(
    code: str,
    request: Request,
    db: AsyncSession = Depends(get_db)
):
    """Handle GitHub OAuth callback"""
    # Exchange code for user info
    user_info = await GitHubOAuth.exchange_code(code)
    
    if not user_info or not user_info.get("email"):
        return RedirectResponse(
            url=f"{settings.frontend_url}/login?error=github_auth_failed"
        )
    
    # Find or create user
    result = await db.execute(
        select(User).where(User.email == user_info["email"])
    )
    user = result.scalar_one_or_none()
    
    if user:
        # Update OAuth info if needed
        if user.oauth_provider == OAuthProvider.LOCAL.value:
            user.oauth_provider = OAuthProvider.GITHUB.value
            user.oauth_id = user_info.get("oauth_id")
        if not user.avatar_url and user_info.get("picture"):
            user.avatar_url = user_info["picture"]
        user.is_verified = True
    else:
        # Create new user
        user = User(
            email=user_info["email"],
            first_name=user_info.get("first_name"),
            last_name=user_info.get("last_name"),
            avatar_url=user_info.get("picture"),
            is_verified=True,
            oauth_provider=OAuthProvider.GITHUB.value,
            oauth_id=user_info.get("oauth_id")
        )
        db.add(user)
        await db.flush()
    
    # Create tokens
    tokens = await create_tokens_for_user(db, user, request)
    await db.commit()
    
    # Redirect to frontend with tokens
    redirect_url = (
        f"{settings.frontend_url}/auth/callback"
        f"?access_token={tokens.access_token}"
        f"&refresh_token={tokens.refresh_token}"
        f"&provider=github"
    )
    return RedirectResponse(url=redirect_url)


# ============ User Info ============

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """Get current authenticated user info"""
    return UserResponse.model_validate(current_user)
