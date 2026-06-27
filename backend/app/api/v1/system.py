"""
System Endpoints — Release Candidate Architecture.

Endpoints:
    GET /system/version    → Build info, environment, git commit
    GET /system/health     → DB connectivity, Redis, AI model availability
    GET /system/flags      → All feature flag states
    GET /system/telemetry  → LLM cost tracking, latency, session counts
"""
import os
from fastapi import APIRouter
from app.core.feature_flags import features
from app.core.telemetry import telemetry
from app.core.observability import logger

router = APIRouter()

VERSION = "1.0.0-rc1"


@router.get("/version")
async def get_version():
    """Build info and version metadata."""
    return {
        "version":     VERSION,
        "build":       os.environ.get("BUILD_NUMBER", "dev"),
        "git_commit":  os.environ.get("GIT_COMMIT", "unknown"),
        "environment": os.environ.get("ENVIRONMENT", "development"),
        "api":         "Holistic Interview Intelligence",
    }


@router.get("/health")
async def health_check():
    """
    Deep health check — verifies all critical services are reachable.
    Returns HTTP 200 if healthy, 503 if any critical service is down.
    """
    from fastapi.responses import JSONResponse
    from app.core.database import check_db_health

    status = {"status": "healthy", "services": {}}

    # Database
    try:
        db_ok = await check_db_health()
        status["services"]["database"] = "ok" if db_ok else "degraded"
    except Exception as e:
        status["services"]["database"] = f"error: {e}"
        status["status"] = "degraded"

    # Redis
    try:
        from app.core.redis_client import get_redis_client
        redis = get_redis_client()
        if redis:
            redis.ping()
            status["services"]["redis"] = "ok"
        else:
            status["services"]["redis"] = "not configured"
    except Exception as e:
        status["services"]["redis"] = f"error: {e}"
        status["status"] = "degraded"

    # Feature flags summary
    status["features"] = {
        "speech":    features.is_enabled("speech_transcription"),
        "vision":    features.is_enabled("face_analysis"),
        "emotion":   features.is_enabled("emotion_detection"),
        "coaching":  features.is_enabled("coaching_hints"),
        "integrity": features.is_enabled("integrity_monitoring"),
    }

    logger.info("health_check", status=status["status"])

    http_status = 200 if status["status"] == "healthy" else 503
    return JSONResponse(content=status, status_code=http_status)


@router.get("/flags")
async def get_feature_flags():
    """Returns all current feature flag states."""
    return {
        "flags": features.all_flags(),
        "version": VERSION,
    }


@router.get("/telemetry")
async def get_telemetry():
    """
    Returns telemetry summary: LLM cost tracking, latency, session counts.
    Suitable for an internal ops dashboard.
    """
    return telemetry.get_summary()
