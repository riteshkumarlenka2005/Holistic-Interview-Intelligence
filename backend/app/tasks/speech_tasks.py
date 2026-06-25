"""
Celery task for processing audio chunks.
Uses SpeechEngine (faster-whisper) for server-side transcription.
"""
import os
import base64
import tempfile
from app.core.celery_app import celery_app


@celery_app.task(bind=True, max_retries=3, queue="speech")
def process_audio_chunk(self, session_id: str, timestamp_ms: int, audio_data: str):
    """
    Receives a base64-encoded audio chunk, writes it to a temp file,
    and runs it through the SpeechEngine.
    
    Args:
        session_id: The interview session ID.
        timestamp_ms: Timestamp of the audio chunk in milliseconds.
        audio_data: Base64-encoded audio bytes.
    """
    try:
        from app.services.speech_engine import SpeechEngine

        # Decode audio from base64
        audio_bytes = base64.b64decode(audio_data)

        # Write to temp file (faster-whisper expects a file path)
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp.write(audio_bytes)
            tmp_path = tmp.name

        try:
            engine = SpeechEngine()
            result = engine.analyze(tmp_path)
        finally:
            os.unlink(tmp_path)  # Always clean up

        # Store result in Redis for accumulation (keyed by session + timestamp)
        from app.core.redis_client import get_redis
        import json
        redis_client = get_redis()
        key = f"speech:{session_id}:chunks"
        payload = {"timestamp_ms": timestamp_ms, **result}
        redis_client.rpush(key, json.dumps(payload))
        redis_client.expire(key, 3600)  # TTL of 1 hour

        return {"status": "ok", "session_id": session_id, "wpm": result.get("wpm")}

    except Exception as exc:
        raise self.retry(exc=exc, countdown=5)


@celery_app.task(bind=True, max_retries=2, queue="speech")
def finalize_speech_analysis(self, session_id: str):
    """
    Called at end of session. Aggregates all speech chunks into a final SpeechMetrics record.
    """
    try:
        import json
        from app.core.redis_client import get_redis

        redis_client = get_redis()
        key = f"speech:{session_id}:chunks"
        raw_chunks = redis_client.lrange(key, 0, -1)

        if not raw_chunks:
            return {"status": "no_chunks", "session_id": session_id}

        chunks = [json.loads(c) for c in raw_chunks]

        # Aggregate
        total_words = sum(c.get("word_count", 0) for c in chunks)
        total_duration = sum(c.get("duration_seconds", 0) for c in chunks)
        total_fillers = sum(c.get("filler_count", 0) for c in chunks)
        avg_fluency = sum(c.get("fluency_score", 0) for c in chunks) / len(chunks)

        agg_wpm = round((total_words / (total_duration / 60)), 1) if total_duration > 0 else 0
        filler_rate = round((total_fillers / total_words) * 100, 1) if total_words > 0 else 0

        return {
            "status": "completed",
            "session_id": session_id,
            "total_words": total_words,
            "total_duration_seconds": round(total_duration, 2),
            "avg_wpm": agg_wpm,
            "total_filler_count": total_fillers,
            "filler_rate_percent": filler_rate,
            "avg_fluency_score": round(avg_fluency, 1),
            "chunk_count": len(chunks),
        }

    except Exception as exc:
        raise self.retry(exc=exc, countdown=10)
