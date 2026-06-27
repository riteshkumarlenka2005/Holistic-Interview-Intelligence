"""
Speech Analysis WebSocket Endpoint (Phase 4)
Real-time streaming of speech analysis results using SpeechIntelligenceEngine.
"""
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, UploadFile, File
from typing import Dict, Optional
import json
import asyncio
import base64
import tempfile
import os
from datetime import datetime
from app.services.speech_engine import SpeechIntelligenceEngine

router = APIRouter()

active_speech_sessions: Dict[str, Dict] = {}


@router.websocket("/ws/speech-analysis/{session_id}")
async def speech_analysis_websocket(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time speech analysis (Hybrid Streaming Architecture).
    """
    await websocket.accept()
    
    active_speech_sessions[session_id] = {
        "connected_at": datetime.now().isoformat(),
        "chunks_processed": 0,
        "websocket": websocket
    }
    
    engine = SpeechIntelligenceEngine()
    
    # We will accumulate the audio into a temporary file for Whisper
    tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    
    try:
        await websocket.send_json({
            "type": "connected",
            "session_id": session_id,
            "message": "Speech Intelligence Engine ready"
        })
        
        while True:
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=60.0
                )
                
                message = json.loads(data)
                msg_type = message.get("type", "")
                
                if msg_type == "audio":
                    base64_data = message.get("data", "")
                    
                    if base64_data:
                        # Append to our accumulating audio file
                        try:
                            if ',' in base64_data:
                                base64_data = base64_data.split(',')[1]
                            chunk_bytes = base64.b64decode(base64_data)
                            tmp_file.write(chunk_bytes)
                            tmp_file.flush()
                        except Exception as e:
                            print(f"Error decoding base64 audio: {e}")
                            continue

                        # Run partial analysis on the accumulated audio
                        loop = asyncio.get_event_loop()
                        try:
                            result = await loop.run_in_executor(
                                None,
                                engine.analyze_audio,
                                tmp_file.name,
                                True # is_partial = True
                            )
                            
                            active_speech_sessions[session_id]["chunks_processed"] += 1
                            
                            await websocket.send_json({
                                "type": "analysis",
                                **result
                            })
                        except Exception as e:
                            print(f"[SpeechEngine] Partial analysis error: {e}")
                
                elif msg_type == "ping":
                    await websocket.send_json({"type": "pong"})
                
                elif msg_type == "get_summary" or msg_type == "finalize":
                    # Run final authoritative analysis
                    loop = asyncio.get_event_loop()
                    try:
                        result = await loop.run_in_executor(
                            None,
                            engine.analyze_audio,
                            tmp_file.name,
                            False # is_partial = False
                        )
                        
                        await websocket.send_json({
                            "type": "summary",
                            **result
                        })
                    except Exception as e:
                        print(f"[SpeechEngine] Final analysis error: {e}")
                
                elif msg_type == "reset":
                    # Clear out the temporary file for the next answer
                    tmp_file.close()
                    os.unlink(tmp_file.name)
                    tmp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
                    
                    await websocket.send_json({
                        "type": "reset_confirmed",
                        "message": "Speech session reset"
                    })
                    
            except asyncio.TimeoutError:
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
        if session_id in active_speech_sessions:
            del active_speech_sessions[session_id]
        
        # Always cleanup temp file
        try:
            tmp_file.close()
            os.unlink(tmp_file.name)
        except Exception:
            pass

@router.get("/sessions")
async def list_active_speech_sessions():
    sessions = []
    for session_id, info in active_speech_sessions.items():
        sessions.append({
            "session_id": session_id,
            "connected_at": info.get("connected_at"),
            "chunks_processed": info.get("chunks_processed", 0)
        })
    return {"active_sessions": sessions, "count": len(sessions)}
