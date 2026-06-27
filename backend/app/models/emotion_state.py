from dataclasses import dataclass, field
from typing import List, Dict
from collections import deque

@dataclass
class EmotionState:
    current_emotion: str = "neutral"
    emotion_history: List[Dict[str, float]] = field(default_factory=list)
    emotion_score: float = 0.0
    last_analysis_time: float = 0.0
    last_coaching_time: float = 0.0
    confidence: float = 0.0
    timeline: deque = field(default_factory=lambda: deque(maxlen=300))
