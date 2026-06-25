"""
Vision Tasks.
Processes video frames through FaceEngine and EyeEngine in the background.
Tracks rolling metrics and triggers CoachingEngine.
"""
import os
import base64
import json
import time
from app.core.celery_app import celery_app
from app.core.redis_client import get_redis


@celery_app.task(bind=True, max_retries=2, queue="vision")
def process_video_chunk(self, session_id: str, timestamp_ms: int, frame_base64: str):
    """
    Decodes a base64 frame, runs it through FaceEngine and EyeEngine,
    stores results in Redis, and runs CoachingEngine.
    """
    try:
        import cv2
        import numpy as np
        from app.services.face_engine import FaceEngine
        from app.services.eye_engine import EyeEngine
        from app.services.coaching_engine import CoachingEngine

        # Decode base64 to numpy array
        img_data = base64.b64decode(frame_base64)
        np_arr = np.frombuffer(img_data, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        if img is None:
            return {"status": "error", "message": "Failed to decode frame"}

        # Run engines
        face_engine = FaceEngine()
        eye_engine = EyeEngine()

        face_metrics = face_engine.analyze_frame(img)
        eye_metrics = eye_engine.analyze_frame(img)

        # Combine metrics
        frame_metrics = {
            "timestamp_ms": timestamp_ms,
            **face_metrics,
            **eye_metrics
        }

        # Store in Redis
        redis_client = get_redis()
        frames_key = f"vision:{session_id}:frames"
        redis_client.rpush(frames_key, json.dumps(frame_metrics))
        redis_client.expire(frames_key, 3600)  # 1 hour TTL

        # -------------------------------------------------------------
        # Calculate Rolling Metrics for Coaching Engine
        # -------------------------------------------------------------
        # Fetch the last 15 frames (approx 3 seconds at 5fps)
        recent_frames_raw = redis_client.lrange(frames_key, -15, -1)
        recent_frames = [json.loads(f) for f in recent_frames_raw]

        if recent_frames:
            # Aggregate metrics over recent window
            rolling_face = face_engine.aggregate_session_metrics(recent_frames)
            rolling_eye = eye_engine.aggregate_session_metrics(recent_frames, fps=5)

            rolling_metrics = {
                "face_count": face_metrics["face_count"], # use instantaneous for multiple faces
                "eye_contact_percent": rolling_eye["eye_contact_percent"],
                "head_stability_score": rolling_face["head_stability_score"],
                "avg_engagement": rolling_face["avg_engagement"]
            }

            # Add latest speech metrics if available for full coaching context
            speech_key = f"speech:{session_id}:chunks"
            latest_speech_raw = redis_client.lindex(speech_key, -1)
            if latest_speech_raw:
                speech_data = json.loads(latest_speech_raw)
                rolling_metrics["filler_rate_percent"] = speech_data.get("filler_rate_percent", 0)
                rolling_metrics["wpm"] = speech_data.get("wpm", 0)

            # Run CoachingEngine
            coaching_engine = CoachingEngine()
            hints = coaching_engine.check_metrics(session_id, rolling_metrics)

            if hints:
                import socketio
                from app.core.config import get_settings
                settings = get_settings()
                mgr = socketio.RedisManager(settings.REDIS_URL, write_only=True)
                
                for hint in hints:
                    # Emit 'coaching_hint' event to the specific room (session_id)
                    mgr.emit('coaching_hint', data=hint, room=session_id, namespace='/interview')

        return {"status": "ok", "session_id": session_id}

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)


@celery_app.task(bind=True, max_retries=2, queue="vision")
def finalize_vision_analysis(self, session_id: str):
    """
    Called at end of session (or end of an answer).
    Aggregates all vision frames into final metrics for the Confidence Engine.
    """
    try:
        from app.services.face_engine import FaceEngine
        from app.services.eye_engine import EyeEngine

        redis_client = get_redis()
        frames_key = f"vision:{session_id}:frames"
        raw_frames = redis_client.lrange(frames_key, 0, -1)

        if not raw_frames:
            return {"status": "no_frames", "session_id": session_id}

        frames = [json.loads(f) for f in raw_frames]

        face_engine = FaceEngine()
        eye_engine = EyeEngine()

        face_agg = face_engine.aggregate_session_metrics(frames)
        eye_agg = eye_engine.aggregate_session_metrics(frames, fps=5)

        # Clear the frames for the next answer to start fresh (if called per-answer)
        redis_client.delete(frames_key)

        return {
            "status": "completed",
            "session_id": session_id,
            "face_metrics": face_agg,
            "eye_metrics": eye_agg,
            "frame_count": len(frames)
        }

    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
