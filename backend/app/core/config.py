"""
Application configuration management
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from pydantic import field_validator
from functools import lru_cache
from typing import Optional, List


class Settings(BaseSettings):
    # Application
    app_env: str = "development"
    app_name: str = "Holistic Interview Intelligence"
    debug: bool = False
    frontend_url: str = "http://localhost:4321"
    backend_url: str = "http://localhost:8000"
    
    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/interview_db"
    
    # Database Pool Settings (for PostgreSQL)
    database_pool_size: int = 20
    database_max_overflow: int = 10
    database_pool_timeout: int = 30
    database_pool_recycle: int = 3600
    db_echo: bool = False
    
    # Redis
    redis_url: str = "redis://localhost:6379"

    # Celery
    celery_broker_url: str = "redis://localhost:6379/0"
    celery_result_backend: str = "redis://localhost:6379/1"
    worker_concurrency: int = 4

    # JWT Configuration
    secret_key: str = "dev-secret-key-change-in-production-holistic-interview-2026"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    
    # CORS
    cors_origins: str | List[str] = [
        "http://localhost:4321",
        "http://localhost:3000",
        "http://127.0.0.1:4321",
        "http://127.0.0.1:3000"
    ]

    @field_validator("cors_origins", mode="before")
    def assemble_cors_origins(cls, v: str | List[str]) -> List[str]:
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    # AI Providers
    ai_provider: str = "gemini"  # openai | gemini | claude
    openai_api_key: str = ""
    gemini_api_key: str = ""
    anthropic_api_key: str = ""

    # Text-to-Speech
    tts_provider: str = "openai"  # openai | elevenlabs | browser
    elevenlabs_api_key: str = ""

    # AI Services (Internal Python API)
    ai_service_url: str = "http://localhost:8001"
    ai_service_timeout: int = 60
    
    # Storage
    storage_provider: str = "supabase"
    supabase_url: str = ""
    supabase_service_key: str = ""
    supabase_bucket: str = "hii-media"
    
    aws_access_key_id: str = ""
    aws_secret_access_key: str = ""
    aws_s3_bucket: str = ""
    aws_s3_region: str = "ap-south-1"
    max_upload_size_mb: int = 500

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/v1/auth/google/callback"
    
    # GitHub OAuth
    github_client_id: str = ""
    github_client_secret: str = ""
    github_redirect_uri: str = "http://localhost:8000/v1/auth/github/callback"
    
    # SMTP Configuration
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_username: str = ""
    smtp_password: str = ""
    smtp_from_email: str = "noreply@interviewai.local"
    smtp_from_name: str = "HII Interview Platform"
    smtp_use_tls: bool = True
    
    # OTP Configuration
    otp_expire_minutes: int = 5
    otp_length: int = 6
    
    # Monitoring
    sentry_dsn: str = ""
    flower_port: int = 5555
    enable_prometheus: bool = True

    # Rate Limiting
    rate_limit_auth: str = "10/15minutes"
    rate_limit_api: str = "100/minute"
    rate_limit_analysis: str = "5/minute"
    
    # Feature Flags
    enable_coaching: bool = True
    enable_face_analysis: bool = True
    enable_eye_tracking: bool = True
    enable_playback: bool = True
    
    # Phase 6 Feature Flags
    enable_realtime_coaching: bool = True
    enable_emotion: bool = True
    enable_tts: bool = True
    enable_partial_whisper: bool = True
    enable_gemini: bool = True
    
    # Dialogue Manager & Coaching Constants
    dialogue_queue_ttl: int = 10
    coaching_cooldown: int = 20
    partial_analysis_interval: int = 3
    max_filler_words: int = 5
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database"""
        return "sqlite" in self.database_url.lower()
    
    @property
    def is_postgres(self) -> bool:
        """Check if using PostgreSQL database"""
        return "postgresql" in self.database_url.lower()

    # Uppercase aliases expected by various modules
    @property
    def REDIS_URL(self) -> str:
        return self.redis_url

    @property
    def SECRET_KEY(self) -> str:
        return self.secret_key

    @property
    def API_V1_STR(self) -> str:
        return "/v1"

    @property
    def ALGORITHM(self) -> str:
        return self.algorithm
    
    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).resolve().parent.parent.parent / ".env"),
        extra="allow",
        case_sensitive=False
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()


# Module-level singleton — imported as `from app.core.config import settings`
settings = get_settings()
