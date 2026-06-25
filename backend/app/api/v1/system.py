from fastapi import APIRouter
import os

router = APIRouter()

@router.get("/version")
async def get_version():
    """Get system version and build information"""
    return {
        "version": "1.0.0-rc1",
        "build": os.environ.get("BUILD_NUMBER", "dev"),
        "git_commit": os.environ.get("GIT_COMMIT", "unknown"),
        "environment": os.environ.get("ENVIRONMENT", "development")
    }
