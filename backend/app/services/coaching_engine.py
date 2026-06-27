"""
Coaching Engine — Real-Time Interview Guidance.

Runs continuously during the interview session.
Checks live metrics against thresholds and emits coaching hints via WebSocket.

Hint Severity:
    CRITICAL → Must act now (e.g., multiple faces — integrity violation)
    WARNING  → Should improve (e.g., poor eye contact)
    INFO     → Nice to fix (e.g., speaking pace)

Cooldown: 15 seconds per hint type to prevent spam.

Hints produced:
    1. Multiple faces detected   (CRITICAL)
    2. Low eye contact           (WARNING)
    3. Too many filler words     (WARNING)
    4. Speaking too fast         (INFO)
    5. Speaking too slow         (INFO)
    6. Head movement / jitter    (INFO)
    7. Low volume / speak louder (INFO)
"""
import time
import enum
from typing import Dict, Any, List


class CoachingSeverity(str, enum.Enum):
    INFO     = "info"
    WARNING  = "warning"
    CRITICAL = "critical"


class CoachingHint:
    def __init__(self, message: str, severity: CoachingSeverity, metric: str):
        self.message  = message
        self.severity = severity
        self.metric   = metric
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message":   self.message,
            "severity":  self.severity.value,
            "metric":    self.metric,
            "timestamp": self.timestamp,
        }


class CoachingEngine:
    COOLDOWN_SECONDS = 15  # Per-metric cooldown to avoid spamming
    EMOTION_COOLDOWN_SECONDS = 20 # Longer cooldown for emotional hints

    # Thresholds
    LOW_EYE_CONTACT_THRESHOLD   = 40   # % below this triggers warning
    HIGH_FILLER_RATE_THRESHOLD  = 10   # % above this triggers warning
    TOO_FAST_WPM                = 180  # words per minute
    TOO_SLOW_WPM                = 80
    LOW_HEAD_STABILITY_THRESHOLD = 40  # score below this triggers info
    LOW_VOLUME_THRESHOLD         = 50  # rms energy below this triggers hint

    def __init__(self):
        # session_id → { metric → last_triggered_timestamp }
        self._last_triggered: Dict[str, Dict[str, float]] = {}

    def _can_trigger(self, session_id: str, metric: str, custom_cooldown: int = None) -> bool:
        """Returns True if cooldown has elapsed for this metric in this session."""
        session = self._last_triggered.setdefault(session_id, {})
        last = session.get(metric, 0)
        cooldown = custom_cooldown if custom_cooldown is not None else self.COOLDOWN_SECONDS
        if time.time() - last >= cooldown:
            session[metric] = time.time()
            return True
        return False

    def check_metrics(self, session_id: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Evaluates real-time metrics and produces coaching hints.

        Expected metrics keys (all optional — engine handles missing gracefully):
            face_count          (int)
            eye_contact_percent (float 0-100)
            filler_rate_percent (float 0-100)
            wpm                 (float)
            head_stability_score(float 0-100)
            volume_rms          (float 0-100, from audio processing)

        Returns:
            List of hint dicts ready to emit over WebSocket.
        """
        hints = []
        
        # Extract metrics for combined scoring
        eye = metrics.get("eye_contact_percent")
        stability = metrics.get("head_stability_score")
        emotion = metrics.get("emotion")
        emotion_conf = metrics.get("emotion_confidence", 0.0)

        # ---------------------------------------------------------------------
        # Emotion & Behavioral Combined Coaching
        # ---------------------------------------------------------------------
        if emotion == "happy" and emotion_conf >= 50.0:
            if self._can_trigger(session_id, "emotion_happy", self.EMOTION_COOLDOWN_SECONDS):
                hints.append(CoachingHint(
                    message="Great smile! It shows confidence.",
                    severity=CoachingSeverity.INFO,
                    metric="emotion_happy",
                ).to_dict())
                
        elif emotion in ["fear", "sad", "nervous"] and emotion_conf >= 50.0:
            # Combined Confidence Score: Only trigger if they also look away or fidget
            if (eye is not None and eye < 60) or (stability is not None and stability < 60):
                if self._can_trigger(session_id, "emotion_nervous", self.EMOTION_COOLDOWN_SECONDS):
                    hints.append(CoachingHint(
                        message="Take a deep breath. You're doing great.",
                        severity=CoachingSeverity.INFO,
                        metric="emotion_nervous",
                    ).to_dict())

        # 1. Multiple faces — CRITICAL (integrity concern)
        if metrics.get("face_count", 1) > 1:
            if self._can_trigger(session_id, "multiple_faces"):
                hints.append(CoachingHint(
                    message="Multiple faces detected. Please ensure you are alone.",
                    severity=CoachingSeverity.CRITICAL,
                    metric="multiple_faces",
                ).to_dict())

        # 2. Low eye contact — WARNING
        eye = metrics.get("eye_contact_percent")
        if eye is not None and eye < self.LOW_EYE_CONTACT_THRESHOLD:
            if self._can_trigger(session_id, "eye_contact"):
                hints.append(CoachingHint(
                    message="Maintain eye contact with the camera.",
                    severity=CoachingSeverity.WARNING,
                    metric="eye_contact",
                ).to_dict())

        # 3. Filler words — WARNING
        filler_rate = metrics.get("filler_rate_percent")
        if filler_rate is not None and filler_rate > self.HIGH_FILLER_RATE_THRESHOLD:
            if self._can_trigger(session_id, "filler_rate"):
                hints.append(CoachingHint(
                    message="Try to reduce filler words like 'um', 'uh', 'like', 'basically'.",
                    severity=CoachingSeverity.WARNING,
                    metric="filler_rate",
                ).to_dict())

        # 4. Speaking too fast — INFO
        wpm = metrics.get("wpm")
        if wpm is not None and wpm > self.TOO_FAST_WPM:
            if self._can_trigger(session_id, "pace_fast"):
                hints.append(CoachingHint(
                    message="You're speaking a bit fast. Slow down slightly for clarity.",
                    severity=CoachingSeverity.INFO,
                    metric="pace_fast",
                ).to_dict())

        # 5. Speaking too slow — INFO
        elif wpm is not None and 0 < wpm < self.TOO_SLOW_WPM:
            if self._can_trigger(session_id, "pace_slow"):
                hints.append(CoachingHint(
                    message="Your pace is a bit slow. Try to speak a bit faster.",
                    severity=CoachingSeverity.INFO,
                    metric="pace_slow",
                ).to_dict())

        # 6. Head jitter / instability — INFO
        if stability is not None and stability < self.LOW_HEAD_STABILITY_THRESHOLD:
            if self._can_trigger(session_id, "head_stability"):
                hints.append(CoachingHint(
                    message="Try to keep your head steady while speaking.",
                    severity=CoachingSeverity.INFO,
                    metric="head_stability",
                ).to_dict())

        # 7. Low volume / speak louder — INFO
        volume = metrics.get("volume_rms")
        if volume is not None and volume < self.LOW_VOLUME_THRESHOLD:
            if self._can_trigger(session_id, "volume_low"):
                hints.append(CoachingHint(
                    message="Speak louder — your voice is too quiet.",
                    severity=CoachingSeverity.INFO,
                    metric="volume_low",
                ).to_dict())

        return hints

    def clear_session(self, session_id: str) -> None:
        """Cleans up cooldown state when a session ends."""
        self._last_triggered.pop(session_id, None)
