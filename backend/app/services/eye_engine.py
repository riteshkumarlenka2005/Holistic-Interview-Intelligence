"""
Eye Tracking Engine.
Uses provided MediaPipe FaceMesh landmarks to estimate gaze direction and detect blinks.
Stateless sub-engine.
"""
from typing import Dict, Any, List
import math

class EyeEngine:
    def __init__(self):
        # MediaPipe Landmark Indices
        # Left eye bounding box
        self.LEFT_EYE_LEFT = 33
        self.LEFT_EYE_RIGHT = 133
        self.LEFT_EYE_TOP = 159
        self.LEFT_EYE_BOTTOM = 145
        self.LEFT_IRIS = 468  # Requires refine_landmarks=True

        # Right eye bounding box
        self.RIGHT_EYE_LEFT = 362
        self.RIGHT_EYE_RIGHT = 263
        self.RIGHT_EYE_TOP = 386
        self.RIGHT_EYE_BOTTOM = 374
        self.RIGHT_IRIS = 473 # Requires refine_landmarks=True

    def _calculate_distance(self, p1, p2, iw, ih) -> float:
        x1, y1 = p1.x * iw, p1.y * ih
        x2, y2 = p2.x * iw, p2.y * ih
        return math.hypot(x2 - x1, y2 - y1)

    def _calculate_gaze_ratios(self, landmarks, iw, ih) -> tuple[float, float]:
        """
        Estimates horizontal and vertical gaze direction by comparing the iris center
        relative to the eye corners (horizontal) and eyelids (vertical).
        Returns (gaze_ratio_x, gaze_ratio_y).
        ~0.5 means looking straight.
        """
        # We use the left eye for gaze estimation as a proxy
        p_left = landmarks.landmark[self.LEFT_EYE_LEFT]
        p_right = landmarks.landmark[self.LEFT_EYE_RIGHT]
        p_top = landmarks.landmark[self.LEFT_EYE_TOP]
        p_bottom = landmarks.landmark[self.LEFT_EYE_BOTTOM]
        p_iris = landmarks.landmark[self.LEFT_IRIS]

        # Convert to pixel coordinates
        x_left, y_left = int(p_left.x * iw), int(p_left.y * ih)
        x_right, y_right = int(p_right.x * iw), int(p_right.y * ih)
        x_top, y_top = int(p_top.x * iw), int(p_top.y * ih)
        x_bottom, y_bottom = int(p_bottom.x * iw), int(p_bottom.y * ih)
        x_iris, y_iris = int(p_iris.x * iw), int(p_iris.y * ih)

        eye_width = x_right - x_left
        eye_height = y_bottom - y_top

        gaze_ratio_x = 0.5
        gaze_ratio_y = 0.5

        if eye_width != 0:
            iris_offset_x = x_iris - x_left
            gaze_ratio_x = iris_offset_x / eye_width

        if eye_height != 0:
            iris_offset_y = y_iris - y_top
            gaze_ratio_y = iris_offset_y / eye_height

        return gaze_ratio_x, gaze_ratio_y

    def _calculate_ear(self, landmarks, iw, ih) -> float:
        """
        Calculates Eye Aspect Ratio (EAR) for blink detection.
        """
        # Left eye
        p_left_l = landmarks.landmark[self.LEFT_EYE_LEFT]
        p_right_l = landmarks.landmark[self.LEFT_EYE_RIGHT]
        p_top_l = landmarks.landmark[self.LEFT_EYE_TOP]
        p_bottom_l = landmarks.landmark[self.LEFT_EYE_BOTTOM]

        # Right eye
        p_left_r = landmarks.landmark[self.RIGHT_EYE_LEFT]
        p_right_r = landmarks.landmark[self.RIGHT_EYE_RIGHT]
        p_top_r = landmarks.landmark[self.RIGHT_EYE_TOP]
        p_bottom_r = landmarks.landmark[self.RIGHT_EYE_BOTTOM]

        # Distances
        left_vert = self._calculate_distance(p_top_l, p_bottom_l, iw, ih)
        left_horz = self._calculate_distance(p_left_l, p_right_l, iw, ih)
        
        right_vert = self._calculate_distance(p_top_r, p_bottom_r, iw, ih)
        right_horz = self._calculate_distance(p_left_r, p_right_r, iw, ih)

        ear_left = left_vert / left_horz if left_horz != 0 else 0.0
        ear_right = right_vert / right_horz if right_horz != 0 else 0.0

        return (ear_left + ear_right) / 2.0

    def analyze_landmarks(self, landmarks, iw: int, ih: int) -> Dict[str, Any]:
        """
        Calculates gaze ratios and Eye Aspect Ratio (EAR).
        """
        # We need 468 landmarks for Iris tracking. Fallback if not available.
        if len(landmarks.landmark) < 469:
            return {
                "is_looking_at_camera": False,
                "gaze_ratio_x": 0.5,
                "gaze_ratio_y": 0.5,
                "is_blinking": False,
                "ear": 0.0
            }

        gaze_ratio_x, gaze_ratio_y = self._calculate_gaze_ratios(landmarks, iw, ih)
        ear = self._calculate_ear(landmarks, iw, ih)
        
        # Blink detection threshold
        # Typical EAR for open eye is ~0.25 to 0.35. Blinking drops EAR below 0.20
        is_blinking = ear < 0.20

        # Tolerance: 0.40 to 0.60 is generally looking towards the camera center
        # We check both X and Y now
        is_looking_x = 0.35 <= gaze_ratio_x <= 0.65
        is_looking_y = 0.35 <= gaze_ratio_y <= 0.65
        
        # If they are blinking, they are technically not looking at the camera,
        # but a quick blink shouldn't penalize eye contact immediately.
        # We handle this in aggregation.
        is_looking = is_looking_x and is_looking_y

        return {
            "is_looking_at_camera": is_looking,
            "gaze_ratio_x": round(gaze_ratio_x, 3),
            "gaze_ratio_y": round(gaze_ratio_y, 3),
            "is_blinking": is_blinking,
            "ear": round(ear, 3)
        }

    def aggregate_session_metrics(self, frames_data: List[Dict[str, Any]], fps: int = 5) -> Dict[str, Any]:
        """
        Aggregates frame data to calculate eye contact %, distraction events, and blink rate.
        A distraction event is looking away continuously for > 8 seconds.
        """
        if not frames_data:
            return {
                "eye_contact_percent": 0.0,
                "distraction_events": 0,
                "blink_count": 0,
                "blinks_per_minute": 0.0
            }

        total_frames = len(frames_data)
        looking_frames = 0
        blink_frames = 0
        
        current_away_streak = 0
        distraction_events = 0
        distraction_frame_threshold = 8 * fps  # 8 seconds

        # Blink debouncing (don't double count slow blinks)
        is_currently_blinking = False
        blink_count = 0

        for frame in frames_data:
            # Handle blinking
            if frame.get("is_blinking", False):
                blink_frames += 1
                if not is_currently_blinking:
                    blink_count += 1
                    is_currently_blinking = True
                
                # Treat blink as looking for eye contact purposes so blinks don't hurt score
                looking_frames += 1
                current_away_streak = 0
            else:
                is_currently_blinking = False
                
                # Handle gaze
                if frame.get("is_looking_at_camera", False):
                    looking_frames += 1
                    current_away_streak = 0
                else:
                    current_away_streak += 1
                    if current_away_streak == distraction_frame_threshold:
                        distraction_events += 1
                        current_away_streak = 0

        eye_contact_percent = (looking_frames / total_frames) * 100
        
        duration_minutes = (total_frames / fps) / 60.0
        blinks_per_minute = blink_count / duration_minutes if duration_minutes > 0 else 0.0

        return {
            "eye_contact_percent": round(eye_contact_percent, 1),
            "distraction_events": distraction_events,
            "blink_count": blink_count,
            "blinks_per_minute": round(blinks_per_minute, 1)
        }
