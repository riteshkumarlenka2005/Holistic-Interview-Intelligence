"""
OTP (One-Time Password) service
"""
import secrets
from datetime import datetime, timedelta
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models import OTPToken, User, OTPType

settings = get_settings()


def generate_otp_code() -> str:
    """Generate a secure 6-digit OTP code"""
    return "".join([str(secrets.randbelow(10)) for _ in range(settings.otp_length)])


async def create_otp_token(
    db: AsyncSession,
    user_id: str,
    otp_type: OTPType
) -> OTPToken:
    """Create a new OTP token for a user"""
    # Invalidate any existing OTPs of the same type
    existing_otps = await db.execute(
        select(OTPToken).where(
            and_(
                OTPToken.user_id == user_id,
                OTPToken.otp_type == otp_type.value,
                OTPToken.used == False
            )
        )
    )
    for otp in existing_otps.scalars():
        otp.used = True
    
    # Create new OTP
    otp_code = generate_otp_code()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.otp_expire_minutes)
    
    otp_token = OTPToken(
        user_id=user_id,
        code=otp_code,
        otp_type=otp_type.value,
        expires_at=expires_at,
        used=False
    )
    
    db.add(otp_token)
    await db.flush()
    
    return otp_token


async def verify_otp(
    db: AsyncSession,
    email: str,
    code: str,
    otp_type: OTPType
) -> tuple[bool, str, User | None]:
    """
    Verify an OTP code
    Returns: (success, message, user)
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return False, "User not found", None
    
    # Find the most recent valid OTP
    result = await db.execute(
        select(OTPToken).where(
            and_(
                OTPToken.user_id == user.id,
                OTPToken.otp_type == otp_type.value,
                OTPToken.used == False
            )
        ).order_by(OTPToken.created_at.desc())
    )
    otp_token = result.scalar_one_or_none()
    
    if not otp_token:
        return False, "No active OTP found. Please request a new code.", None
    
    # Check if expired
    if otp_token.is_expired:
        return False, "OTP has expired. Please request a new code.", None
    
    # Check if code matches
    if otp_token.code != code:
        return False, "Invalid OTP code", None
    
    # Mark OTP as used
    otp_token.used = True
    
    # If this is email verification, mark user as verified
    if otp_type == OTPType.EMAIL_VERIFICATION:
        user.is_verified = True
    
    await db.flush()
    
    return True, "OTP verified successfully", user


async def resend_otp(
    db: AsyncSession,
    email: str,
    otp_type: OTPType
) -> tuple[bool, str, str | None]:
    """
    Resend OTP for a user
    Returns: (success, message, otp_code)
    """
    # Find user by email
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        return False, "User not found", None
    
    # Check rate limiting (no more than 1 OTP per minute)
    result = await db.execute(
        select(OTPToken).where(
            and_(
                OTPToken.user_id == user.id,
                OTPToken.otp_type == otp_type.value,
                OTPToken.created_at > datetime.utcnow() - timedelta(minutes=1)
            )
        )
    )
    recent_otp = result.scalar_one_or_none()
    
    if recent_otp:
        return False, "Please wait at least 1 minute before requesting a new code", None
    
    # Create new OTP
    otp_token = await create_otp_token(db, user.id, otp_type)
    
    return True, "New OTP generated", otp_token.code
