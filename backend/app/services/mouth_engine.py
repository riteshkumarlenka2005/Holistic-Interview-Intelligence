"""
Mouth State Engine.
Uses MediaPipe FaceMesh landmarks to detect if the mouth is open (speaking/smiling).
"""
from typing import Dict, Any, List
import math

class MouthEngine:
    def __init__(self):
        # Mouth landmarks (MediaPipe)
        self.UPPER_LIP = 13
        self.LOWER_LIP = 14
        self.LEFT_MOUTH = 78
        self.RIGHT_MOUTH = 308

    def _calculate_distance(self, p1, p2, iw, ih) -> float:
        x1, y1 = p1.x * iw, p1.y * ih
        x2, y2 = p2.x * iw, p2.y * ih
        return math.hypot(x2 - x1, y2 - y1)

    def analyze_landmarks(self, landmarks, iw: int, ih: int) -> Dict[str, Any]:
        """
        Calculates Mouth Aspect Ratio (MAR).
        """
        p_upper = landmarks.landmark[self.UPPER_LIP]
        p_lower = landmarks.landmark[self.LOWER_LIP]
        p_left = landmarks.landmark[self.LEFT_MOUTH]
        p_right = landmarks.landmark[self.RIGHT_MOUTH]

        vert_dist = self._calculate_distance(p_upper, p_lower, iw, ih)
        horz_dist = self._calculate_distance(p_left, p_right, iw, ih)

        if horz_dist == 0:
            return {"is_mouth_open": False, "mar": 0.0}

        mar = vert_dist / horz_dist
        
        # Typical threshold for open mouth is ~0.15 to 0.20
        is_mouth_open = mar > 0.15

        return {
            "is_mouth_open": is_mouth_open,
            "mar": round(mar, 3)
        }

    def aggregate_session_metrics(self, frames_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculates percentage of time mouth is open.
        """
        if not frames_data:
            return {"mouth_open_percent": 0.0}

        total_frames = len(frames_data)
        open_frames = sum(1 for f in frames_data if f.get("is_mouth_open", False))
        
        return {
            "mouth_open_percent": round((open_frames / total_frames) * 100, 1)
        }
