"""
Vision Analysis - Main Entry Point
Provides FastAPI endpoints for vision analysis services
"""
from __future__ import annotations

from typing import Any, Dict

# Lazy imports for optional heavy dependencies
FastAPI: Any = None
cv2: Any = None


def _load_fastapi() -> Any:
    """Lazy load FastAPI"""
    global FastAPI
    if FastAPI is None:
        try:
            from fastapi import FastAPI as _FastAPI
            FastAPI = _FastAPI
        except ImportError:
            raise ImportError("FastAPI required: pip install fastapi uvicorn")
    return FastAPI


def create_app() -> Any:
    """Create and configure the FastAPI application"""
    _FastAPI = _load_fastapi()
    app = _FastAPI(
        title="Vision Analysis Service",
        description="AI-powered vision analysis for interview preparation",
        version="1.0.0"
    )

    @app.get("/health")
    async def health_check() -> Dict[str, str]:
        return {"status": "healthy", "service": "vision-analysis"}

    @app.post("/analyze/frame")
    async def analyze_frame_endpoint(data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a single video frame"""
        from .pipeline import analyze_frame
        import numpy as np
        import base64

        # Decode frame from base64
        frame_data = base64.b64decode(data.get("frame", ""))
        frame_array = np.frombuffer(frame_data, dtype=np.uint8)

        # Reshape based on provided dimensions
        width = data.get("width", 640)
        height = data.get("height", 480)
        frame = frame_array.reshape((height, width, 3))

        result = analyze_frame(frame)
        return result

    @app.post("/analyze/video")
    async def analyze_video_endpoint(data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze a video file"""
        from .pipeline import analyze_video

        video_path = data.get("video_path", "")
        sample_rate = data.get("sample_rate", 3)

        result = analyze_video(video_path, sample_rate)
        return result

    return app


# Create app instance
app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)
