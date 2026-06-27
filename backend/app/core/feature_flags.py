"""
Feature Flags — Runtime Feature Toggle System.

Allows features to be enabled/disabled without redeployment.
Read from environment variables at startup.

Convention:
    FEATURE_<NAME> = "true" | "false"

Usage:
    from app.core.feature_flags import features

    if features.is_enabled("emotion_detection"):
        result = emotion_engine.analyze(frame)

Adding a new flag:
    1. Add it to FEATURE_DEFAULTS below.
    2. Set FEATURE_<NAME>=true/false in your .env file.
    3. Use features.is_enabled("<name>") in your code.
"""
import os
from typing import Dict


# Default values — all features are ON by default.
# Override in .env: FEATURE_EMOTION_DETECTION=false
FEATURE_DEFAULTS: Dict[str, bool] = {
    # Core AI engines
    "speech_transcription":  True,
    "face_analysis":         True,
    "eye_tracking":          True,
    "emotion_detection":     True,
    "coaching_hints":        True,
    "integrity_monitoring":  True,
    # LLM evaluation
    "technical_evaluation":  True,
    "communication_evaluation": True,
    # Reports
    "report_generation":     True,
    "analytics_dashboard":   True,
    # Advanced (V2)
    "video_recording":       False,   # Requires S3 — off by default
    "resume_parsing":        False,   # V2 feature
    "jd_parsing":            False,   # V2 feature
    # Infrastructure
    "request_id_logging":    True,
    "cost_tracking":         False,   # Requires LLM cost tracking integration
}


class FeatureFlags:
    """
    Reads feature flags from environment variables at startup.
    Environment variables override defaults.
    """

    def __init__(self):
        self._flags: Dict[str, bool] = {}
        for name, default in FEATURE_DEFAULTS.items():
            env_key = f"FEATURE_{name.upper()}"
            env_val = os.environ.get(env_key, "").strip().lower()
            if env_val == "true":
                self._flags[name] = True
            elif env_val == "false":
                self._flags[name] = False
            else:
                self._flags[name] = default

    def is_enabled(self, name: str) -> bool:
        """Returns True if the feature is enabled."""
        return self._flags.get(name, False)

    def all_flags(self) -> Dict[str, bool]:
        """Returns all current flag values (for /health or /debug endpoint)."""
        return dict(self._flags)

    def override(self, name: str, value: bool) -> None:
        """Runtime override — useful for tests."""
        self._flags[name] = value


# Shared singleton — import this everywhere
features = FeatureFlags()
