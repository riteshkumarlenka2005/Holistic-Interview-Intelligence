from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()

@router.get("/features", summary="Get active feature flags")
async def get_feature_flags():
    """
    Returns the current state of feature flags for the frontend.
    """
    return {
        "enable_coaching": settings.enable_coaching,
        "enable_face_analysis": settings.enable_face_analysis,
        "enable_eye_tracking": settings.enable_eye_tracking,
        "enable_playback": settings.enable_playback
    }
