"""
Behavioral Analysis WebSocket Endpoint
Real-time streaming of emotion detection results
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import Dict, Optional
import json
import asyncio
from datetime import datetime
from app.core.redis_client import get_redis

router = APIRouter()

# Track active sessions
active_sessions: Dict[str, Dict] = {}


@router.websocket("/ws/behavioral-analysis/{session_id}")
async def behavioral_analysis_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time behavioral analysis.
    
    Protocol:
    - Client connects with session_id
    - Client sends base64 encoded video frames
    - Server responds with analysis results for each frame
    
    Message format (client -> server):
    {
        "type": "frame",
        "data": "<base64 encoded image>",
        "timestamp": 1234567890.123
    }
    
    Message format (server -> client):
    {
        "type": "analysis",
        "timestamp": 1234567890.123,
        "confidence_score": 0.75,
        "nervousness_score": 0.15,
        "behavioral_tag": "CONFIDENT",
        "emotions": {"happy": 0.1, "neutral": 0.8, ...},
        "face_detected": true,
        "face_box": [x, y, w, h]
    }
    """
    await websocket.accept()
    
    # Initialize session
    active_sessions[session_id] = {
        "connected_at": datetime.now().isoformat(),
        "frames_processed": 0,
        "websocket": websocket
    }
    
    # Lazy import to avoid loading dependencies at startup
    analyzer = None
    
    try:
        from app.services.behavioral_analysis import get_analyzer, analyze_frame_async
        analyzer = get_analyzer()
        analyzer.reset()  # Fresh session
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "Behavioral analysis ready"
        })
        
        while True:
            try:
                # Receive message with timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=30.0
                )
                
                message = json.loads(data)
                msg_type = message.get("type", "")
                
                if msg_type == "frame":
                    # Process video frame
                    base64_data = message.get("data", "")
                    timestamp = message.get("timestamp", 0.0)
                    
                    if base64_data:
                        # Analyze frame
                        result = await analyze_frame_async(base64_data, timestamp)
                        
                        # Update session stats
                        active_sessions[session_id]["frames_processed"] += 1
                        
                        # Fetch latest DeepFace emotion from Redis to emit side-by-side
                        redis_client = get_redis()
                        frames_key = f"vision:{session_id}:frames"
                        latest_raw = redis_client.lindex(frames_key, -1)
                        deepface_data = {"emotion": "neutral", "confidence": 0.0}
                        if latest_raw:
                            try:
                                latest_frame = json.loads(latest_raw)
                                deepface_data = latest_frame.get("deepface", deepface_data)
                            except:
                                pass
                        
                        # Send result back with both FER and DeepFace
                        await websocket.send_json({
                            "type": "analysis",
                            "fer": {
                                "emotion": result.get("behavioral_tag", "NEUTRAL").lower(), # FER maps this
                                "confidence": result.get("confidence_score", 0.0)
                            },
                            "deepface": deepface_data,
                            **result
                        })
                
                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                
                elif msg_type == "get_summary":
                    # Return session summary
                    if analyzer:
                        summary = analyzer.get_session_summary()
                        await websocket.send_json({
                            "type": "summary",
                            **summary
                        })
                
                elif msg_type == "reset":
                    # Reset analyzer for new recording
                    if analyzer:
                        analyzer.reset()
                    await websocket.send_json({
                        "type": "reset_confirmed",
                        "message": "Session reset"
                    })
                    
            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_json({"type": "keepalive"})
                
    except WebSocketDisconnect:
        print(f"Client disconnected from session {session_id}")
        
    except Exception as e:
        print(f"WebSocket error for session {session_id}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
            
    finally:
        # Cleanup session
        if session_id in active_sessions:
            del active_sessions[session_id]


@router.get("/sessions")
async def list_active_sessions():
    """List currently active behavioral analysis sessions"""
    sessions = []
    for session_id, info in active_sessions.items():
        sessions.append({
            "session_id": session_id,
            "connected_at": info.get("connected_at"),
            "frames_processed": info.get("frames_processed", 0)
        })
    return {"active_sessions": sessions, "count": len(sessions)}


@router.post("/analyze-frame")
async def analyze_single_frame(request: dict):
    """
    REST endpoint for single frame analysis (alternative to WebSocket).
    
    Request body:
    {
        "frame": "<base64 encoded image>",
        "timestamp": 1234567890.123
    }
    """
    from app.services.behavioral_analysis import analyze_frame_async
    
    base64_data = request.get("frame", "")
    timestamp = request.get("timestamp", 0.0)
    
    if not base64_data:
        return {"error": "No frame data provided"}
    
    result = await analyze_frame_async(base64_data, timestamp)
    return result
