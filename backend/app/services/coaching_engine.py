"""
Real-Time Coaching Engine.
Processes real-time streams of metrics and emits coaching hints.
Uses cooldowns to avoid spamming the user.
"""
from typing import Dict, Any, List
import time
import enum


class CoachingSeverity(str, enum.Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class CoachingHint:
    def __init__(self, message: str, severity: CoachingSeverity, metric: str):
        self.message = message
        self.severity = severity
        self.metric = metric
        self.timestamp = time.time()

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "severity": self.severity.value,
            "metric": self.metric,
            "timestamp": self.timestamp
        }


class CoachingEngine:
    # 15 seconds cooldown per hint type
    COOLDOWN_SECONDS = 15

    def __init__(self):
        # Maps session_id -> {metric_name -> last_triggered_timestamp}
        self._last_triggered: Dict[str, Dict[str, float]] = {}

    def _can_trigger(self, session_id: str, metric: str) -> bool:
        """Checks if enough time has passed since the last hint for this metric."""
        if session_id not in self._last_triggered:
            self._last_triggered[session_id] = {}
            
        last_time = self._last_triggered[session_id].get(metric, 0)
        current_time = time.time()
        
        if current_time - last_time >= self.COOLDOWN_SECONDS:
            self._last_triggered[session_id][metric] = current_time
            return True
        return False

    def check_metrics(self, session_id: str, metrics: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Takes real-time metrics (e.g. from a chunk) and determines if hints should fire.
        Returns a list of hint dictionaries to be emitted via WebSocket.
        """
        hints = []
        
        # 1. Multiple Faces (CRITICAL)
        if metrics.get("face_count", 1) > 1:
            if self._can_trigger(session_id, "multiple_faces"):
                hints.append(CoachingHint(
                    message="Multiple faces detected. Please ensure you are alone.",
                    severity=CoachingSeverity.CRITICAL,
                    metric="multiple_faces"
                ).to_dict())
                
        # 2. Eye Contact (WARNING)
        # Assuming this is calculated over a rolling window of recent frames
        if "eye_contact_percent" in metrics and metrics["eye_contact_percent"] < 40:
            if self._can_trigger(session_id, "eye_contact"):
                hints.append(CoachingHint(
                    message="Maintain eye contact with the camera.",
                    severity=CoachingSeverity.WARNING,
                    metric="eye_contact"
                ).to_dict())
                
        # 3. Filler Words (WARNING)
        if "filler_rate_percent" in metrics and metrics["filler_rate_percent"] > 10:
            if self._can_trigger(session_id, "filler_rate"):
                hints.append(CoachingHint(
                    message="Try to reduce filler words (um, uh, like).",
                    severity=CoachingSeverity.WARNING,
                    metric="filler_rate"
                ).to_dict())
                
        # 4. Pace (INFO)
        if "wpm" in metrics:
            wpm = metrics["wpm"]
            if wpm > 180:
                if self._can_trigger(session_id, "pace_fast"):
                    hints.append(CoachingHint(
                        message="You're speaking a bit fast. Try slowing down slightly.",
                        severity=CoachingSeverity.INFO,
                        metric="pace_fast"
                    ).to_dict())
            elif wpm > 0 and wpm < 80:
                if self._can_trigger(session_id, "pace_slow"):
                    hints.append(CoachingHint(
                        message="Your pace is a bit slow. Try to speak a bit faster.",
                        severity=CoachingSeverity.INFO,
                        metric="pace_slow"
                    ).to_dict())

        # 5. Head Jitter / Stability (INFO)
        if "head_stability_score" in metrics and metrics["head_stability_score"] < 40:
            if self._can_trigger(session_id, "head_stability"):
                hints.append(CoachingHint(
                    message="Try to keep your head steady.",
                    severity=CoachingSeverity.INFO,
                    metric="head_stability"
                ).to_dict())

        return hints
