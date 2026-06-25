"""
Speech Analysis WebSocket Endpoint
Real-time streaming of speech analysis results
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File
from typing import Dict, Optional
import json
import asyncio
from datetime import datetime

router = APIRouter()

# Track active speech analysis sessions
active_speech_sessions: Dict[str, Dict] = {}


@router.websocket("/ws/speech-analysis/{session_id}")
async def speech_analysis_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time speech analysis.
    
    Protocol:
    - Client connects with session_id
    - Client sends base64 encoded audio chunks
    - Server responds with transcription, grammar, and emotion analysis
    
    Message format (client -> server):
    {
        "type": "audio",
        "data": "<base64 encoded audio>",
        "timestamp": 1234567890.123
    }
    
    Message format (server -> client):
    {
        "type": "analysis",
        "transcription": "I believe this is a great opportunity...",
        "grammar_issues": [{"message": "...", "offset": 5, "length": 4}],
        "emotions": [{"label": "neutral", "score": 0.8}, ...],
        "dominant_emotion": "neutral",
        "filler_count": 2,
        "filler_words": ["um", "like"]
    }
    """
    await websocket.accept()
    
    # Initialize session
    active_speech_sessions[session_id] = {
        "connected_at": datetime.now().isoformat(),
        "chunks_processed": 0,
        "websocket": websocket
    }
    
    # Lazy import to avoid loading dependencies at startup
    analyzer = None
    
    try:
        from app.services.speech_analysis import get_speech_analyzer, analyze_audio_async
        analyzer = get_speech_analyzer()
        analyzer.initialize()  # Preload models
        analyzer.reset()  # Fresh session
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "Speech analysis ready"
        })
        
        while True:
            try:
                # Receive message with timeout
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0  # Longer timeout for audio processing
                )
                
                message = json.loads(data)
                msg_type = message.get("type", "")
                
                if msg_type == "audio":
                    # Process audio chunk
                    base64_data = message.get("data", "")
                    timestamp = message.get("timestamp", 0.0)
                    
                    if base64_data:
                        # Analyze audio
                        result = await analyze_audio_async(base64_data, timestamp)
                        
                        # Update session stats
                        active_speech_sessions[session_id]["chunks_processed"] += 1
                        
                        # Send result back
                        await websocket.send_json({
                            "type": "analysis",
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
                        "message": "Speech session reset"
                    })
                    
            except asyncio.TimeoutError:
                # Send keepalive
                await websocket.send_json({"type": "keepalive"})
                
    except WebSocketDisconnect:
        print(f"Speech client disconnected from session {session_id}")
        
    except Exception as e:
        print(f"Speech WebSocket error for session {session_id}: {e}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": str(e)
            })
        except:
            pass
            
    finally:
        # Cleanup session
        if session_id in active_speech_sessions:
            del active_speech_sessions[session_id]


@router.get("/sessions")
async def list_active_speech_sessions():
    """List currently active speech analysis sessions"""
    sessions = []
    for session_id, info in active_speech_sessions.items():
        sessions.append({
            "session_id": session_id,
            "connected_at": info.get("connected_at"),
            "chunks_processed": info.get("chunks_processed", 0)
        })
    return {"active_sessions": sessions, "count": len(sessions)}


@router.post("/analyze-audio")
async def analyze_audio_file(file: UploadFile = File(...)):
    """
    REST endpoint for audio file analysis (alternative to WebSocket).
    
    Accepts audio file and returns complete speech analysis.
    """
    from app.services.speech_analysis import get_speech_analyzer
    import tempfile
    import os
    
    analyzer = get_speech_analyzer()
    
    # Save uploaded file to temp
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        content = await file.read()
        f.write(content)
        temp_path = f.name
    
    try:
        # Analyze audio
        metrics = analyzer.analyze_audio_bytes(content, timestamp=0.0)
        
        return {
            "transcription": metrics.transcription,
            "word_count": metrics.word_count,
            "grammar_issues": [
                {
                    "message": issue.message,
                    "offset": issue.offset,
                    "length": issue.length,
                    "replacements": issue.replacements
                }
                for issue in metrics.grammar_issues
            ],
            "grammar_error_count": metrics.grammar_error_count,
            "emotions": [
                {"label": e.label, "score": e.score}
                for e in metrics.emotions[:5]
            ],
            "dominant_emotion": metrics.dominant_emotion,
            "filler_count": metrics.filler_count,
            "filler_words": metrics.filler_words
        }
    finally:
        try:
            os.unlink(temp_path)
        except:
            pass


@router.post("/analyze-text")
async def analyze_text(request: dict):
    """
    Analyze text directly (for testing grammar and emotion without audio).
    
    Request body:
    {
        "text": "The text to analyze..."
    }
    """
    from app.services.speech_analysis import get_speech_analyzer
    
    text = request.get("text", "")
    if not text:
        return {"error": "No text provided"}
    
    analyzer = get_speech_analyzer()
    
    # Grammar check
    grammar_issues = analyzer.check_grammar(text)
    
    # Emotion analysis
    emotions = analyzer.analyze_emotions(text)
    
    # Filler detection
    filler_count, filler_words = analyzer.detect_fillers(text)
    
    return {
        "text": text,
        "word_count": len(text.split()),
        "grammar_issues": [
            {
                "message": issue.message,
                "offset": issue.offset,
                "length": issue.length,
                "replacements": issue.replacements
            }
            for issue in grammar_issues
        ],
        "emotions": [
            {"label": e.label, "score": e.score}
            for e in emotions[:5]
        ],
        "dominant_emotion": emotions[0].label if emotions else "neutral",
        "filler_count": filler_count,
        "filler_words": filler_words
    }
