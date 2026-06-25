"""
Email service for sending OTP codes
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import logging

from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


async def send_email(to_email: str, subject: str, html_content: str) -> bool:
    """
    Send an email using SMTP
    Falls back to console logging if SMTP is not configured
    """
    # If SMTP is not configured, log to console
    if not settings.smtp_username or not settings.smtp_password:
        logger.info(f"[EMAIL] To: {to_email}")
        logger.info(f"[EMAIL] Subject: {subject}")
        logger.info(f"[EMAIL] Content: {html_content}")
        print(f"\n{'='*60}")
        print(f"📧 EMAIL (Development Mode)")
        print(f"{'='*60}")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(f"{'='*60}")
        # Extract OTP from content for easy testing
        import re
        otp_match = re.search(r'\b(\d{6})\b', html_content)
        if otp_match:
            print(f"🔑 OTP CODE: {otp_match.group(1)}")
        print(f"{'='*60}\n")
        return True
    
    try:
        # Create message
        message = MIMEMultipart("alternative")
        message["From"] = f"{settings.smtp_from_name} <{settings.smtp_from_email}>"
        message["To"] = to_email
        message["Subject"] = subject
        
        # Attach HTML content
        html_part = MIMEText(html_content, "html")
        message.attach(html_part)
        
        # Send email
        await aiosmtplib.send(
            message,
            hostname=settings.smtp_host,
            port=settings.smtp_port,
            username=settings.smtp_username,
            password=settings.smtp_password,
            start_tls=settings.smtp_use_tls
        )
        
        logger.info(f"Email sent successfully to {to_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send email to {to_email}: {str(e)}")
        return False


async def send_verification_email(to_email: str, otp_code: str, user_name: str = None) -> bool:
    """Send email verification OTP"""
    name = user_name or to_email.split("@")[0]
    
    subject = f"Your Verification Code: {otp_code}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0a0a0f;">
        <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px; padding: 40px; border: 1px solid rgba(124, 58, 237, 0.3);">
                <!-- Logo -->
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #ffffff; font-size: 24px; margin: 0;">
                        <span style="color: #7c3aed;">Interview</span> Intelligence
                    </h1>
                </div>
                
                <!-- Greeting -->
                <h2 style="color: #ffffff; font-size: 22px; margin-bottom: 10px;">
                    Hi {name}! 👋
                </h2>
                
                <p style="color: #a0a0a0; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                    Welcome to Interview Intelligence! Use the verification code below to complete your registration:
                </p>
                
                <!-- OTP Code -->
                <div style="background: linear-gradient(135deg, #7c3aed 0%, #5b21b6 100%); border-radius: 12px; padding: 30px; text-align: center; margin-bottom: 30px;">
                    <p style="color: rgba(255,255,255,0.8); font-size: 14px; margin: 0 0 10px 0; letter-spacing: 1px;">
                        YOUR VERIFICATION CODE
                    </p>
                    <div style="font-size: 36px; font-weight: bold; color: #ffffff; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                        {otp_code}
                    </div>
                </div>
                
                <p style="color: #a0a0a0; font-size: 14px; line-height: 1.6;">
                    ⏰ This code expires in <strong style="color: #7c3aed;">5 minutes</strong>.
                </p>
                
                <p style="color: #a0a0a0; font-size: 14px; line-height: 1.6;">
                    If you didn't request this code, you can safely ignore this email.
                </p>
                
                <!-- Footer -->
                <div style="border-top: 1px solid rgba(255,255,255,0.1); margin-top: 30px; padding-top: 20px; text-align: center;">
                    <p style="color: #666; font-size: 12px; margin: 0;">
                        © 2024 Interview Intelligence. All rights reserved.
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(to_email, subject, html_content)


async def send_password_reset_email(to_email: str, otp_code: str, user_name: str = None) -> bool:
    """Send password reset OTP"""
    name = user_name or to_email.split("@")[0]
    
    subject = f"Password Reset Code: {otp_code}"
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #0a0a0f;">
        <div style="max-width: 600px; margin: 0 auto; padding: 40px 20px;">
            <div style="background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%); border-radius: 16px; padding: 40px; border: 1px solid rgba(239, 68, 68, 0.3);">
                <!-- Logo -->
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #ffffff; font-size: 24px; margin: 0;">
                        <span style="color: #7c3aed;">Interview</span> Intelligence
                    </h1>
                </div>
                
                <!-- Greeting -->
                <h2 style="color: #ffffff; font-size: 22px; margin-bottom: 10px;">
                    Password Reset Request 🔐
                </h2>
                
                <p style="color: #a0a0a0; font-size: 16px; line-height: 1.6; margin-bottom: 30px;">
                    Hi {name}, we received a request to reset your password. Use this code to create a new password:
                </p>
                
                <!-- OTP Code -->
                <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); border-radius: 12px; padding: 30px; text-align: center; margin-bottom: 30px;">
                    <p style="color: rgba(255,255,255,0.8); font-size: 14px; margin: 0 0 10px 0; letter-spacing: 1px;">
                        PASSWORD RESET CODE
                    </p>
                    <div style="font-size: 36px; font-weight: bold; color: #ffffff; letter-spacing: 8px; font-family: 'Courier New', monospace;">
                        {otp_code}
                    </div>
                </div>
                
                <p style="color: #a0a0a0; font-size: 14px; line-height: 1.6;">
                    ⏰ This code expires in <strong style="color: #ef4444;">5 minutes</strong>.
                </p>
                
                <p style="color: #a0a0a0; font-size: 14px; line-height: 1.6;">
                    ⚠️ If you didn't request a password reset, please secure your account immediately.
                </p>
                
                <!-- Footer -->
                <div style="border-top: 1px solid rgba(255,255,255,0.1); margin-top: 30px; padding-top: 20px; text-align: center;">
                    <p style="color: #666; font-size: 12px; margin: 0;">
                        © 2024 Interview Intelligence. All rights reserved.
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return await send_email(to_email, subject, html_content)
