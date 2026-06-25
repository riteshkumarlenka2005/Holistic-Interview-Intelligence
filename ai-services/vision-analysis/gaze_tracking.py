"""
Gaze Tracking Module
Tracks eye movements and eye contact using MediaPipe Face Mesh
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np  # type: ignore[import-untyped]
import time

# Lazy imports
mp: Any = None
cv2: Any = None


def _load_dependencies():
    """Lazy load dependencies"""
    global mp, cv2
    if mp is None:
        try:
            import mediapipe as _mp  # type: ignore[import-untyped]
            import cv2 as _cv2  # type: ignore[import-untyped]
            mp = _mp
            cv2 = _cv2
        except ImportError:
            raise ImportError(
                "MediaPipe and OpenCV required: pip install mediapipe opencv-python"
            )
    return mp, cv2


# Iris landmark indices in MediaPipe Face Mesh (with refine_landmarks=True)
LEFT_IRIS = [468, 469, 470, 471, 472]
RIGHT_IRIS = [473, 474, 475, 476, 477]

# Eye corner indices
LEFT_EYE_INNER = 133
LEFT_EYE_OUTER = 33
RIGHT_EYE_INNER = 362
RIGHT_EYE_OUTER = 263


@dataclass
class GazePoint:
    """Single gaze measurement"""
    timestamp: float
    gaze_direction: Tuple[float, float]  # Normalized (-1 to 1)
    looking_at_camera: bool
    confidence: float
    left_iris_position: Tuple[float, float]
    right_iris_position: Tuple[float, float]


@dataclass
class GazeAnalysis:
    """Complete gaze analysis results"""
    eye_contact_percentage: float
    average_contact_duration: float
    gaze_stability: float  # 0-1, higher = more stable
    looking_away_events: List[Dict]
    heat_map_data: Optional[np.ndarray]
    assessment: str
    recommendations: List[str]


class GazeTracker:
    """
    Real-time gaze tracking using MediaPipe iris landmarks.
    Calculates eye contact, gaze direction, and stability.
    """
    
    # Threshold for considering user is looking at camera
    CENTER_THRESHOLD = 0.15
    
    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5
    ):
        """
        Initialize gaze tracker.
        
        Args:
            min_detection_confidence: Minimum face detection confidence
            min_tracking_confidence: Minimum tracking confidence
        """
        _load_dependencies()
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,  # Required for iris landmarks
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        # History for analysis
        self.gaze_history: List[GazePoint] = []
        self.start_time: Optional[float] = None
    
    def process_frame(
        self,
        frame: np.ndarray,
        timestamp: Optional[float] = None
    ) -> GazePoint:
        """
        Process a single frame for gaze detection.
        
        Args:
            frame: BGR image frame
            timestamp: Optional timestamp (uses current time if not provided)
            
        Returns:
            GazePoint with current gaze information
        """
        if self.start_time is None:
            self.start_time = time.time()
        
        ts = timestamp if timestamp is not None else time.time() - self.start_time
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame.shape[:2]
        
        # Process frame
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            gaze_point = GazePoint(
                timestamp=ts,
                gaze_direction=(0.0, 0.0),
                looking_at_camera=False,
                confidence=0.0,
                left_iris_position=(0.0, 0.0),
                right_iris_position=(0.0, 0.0)
            )
            self.gaze_history.append(gaze_point)
            return gaze_point
        
        landmarks = results.multi_face_landmarks[0]
        
        # Get iris positions
        left_iris = self._get_iris_center(landmarks, LEFT_IRIS, w, h)
        right_iris = self._get_iris_center(landmarks, RIGHT_IRIS, w, h)
        
        # Get eye corners for normalization
        left_inner = self._get_landmark_pos(landmarks, LEFT_EYE_INNER, w, h)
        left_outer = self._get_landmark_pos(landmarks, LEFT_EYE_OUTER, w, h)
        right_inner = self._get_landmark_pos(landmarks, RIGHT_EYE_INNER, w, h)
        right_outer = self._get_landmark_pos(landmarks, RIGHT_EYE_OUTER, w, h)
        
        # Calculate gaze direction (normalized position of iris within eye)
        left_gaze = self._calc_gaze_direction(left_iris, left_inner, left_outer)
        right_gaze = self._calc_gaze_direction(right_iris, right_inner, right_outer)
        
        # Average gaze direction
        gaze_x = (left_gaze[0] + right_gaze[0]) / 2
        gaze_y = (left_gaze[1] + right_gaze[1]) / 2
        
        # Determine if looking at camera (gaze near center)
        gaze_distance = np.sqrt(gaze_x**2 + gaze_y**2)
        looking_at_camera = gaze_distance < self.CENTER_THRESHOLD
        
        # Confidence based on face mesh detection
        confidence = 0.9 if results.multi_face_landmarks else 0.0
        
        gaze_point = GazePoint(
            timestamp=ts,
            gaze_direction=(float(gaze_x), float(gaze_y)),
            looking_at_camera=looking_at_camera,
            confidence=confidence,
            left_iris_position=left_iris,
            right_iris_position=right_iris
        )
        
        self.gaze_history.append(gaze_point)
        return gaze_point
    
    def _get_iris_center(
        self,
        landmarks,
        iris_indices: List[int],
        w: int,
        h: int
    ) -> Tuple[float, float]:
        """Get center of iris from landmarks"""
        points = []
        for idx in iris_indices:
            lm = landmarks.landmark[idx]
            points.append([lm.x * w, lm.y * h])
        center = np.mean(points, axis=0)
        return (float(center[0]), float(center[1]))
    
    def _get_landmark_pos(
        self,
        landmarks,
        idx: int,
        w: int,
        h: int
    ) -> Tuple[float, float]:
        """Get position of a single landmark"""
        lm = landmarks.landmark[idx]
        return (lm.x * w, lm.y * h)
    
    def _calc_gaze_direction(
        self,
        iris: Tuple[float, float],
        inner_corner: Tuple[float, float],
        outer_corner: Tuple[float, float]
    ) -> Tuple[float, float]:
        """
        Calculate normalized gaze direction.
        Returns values from -1 (looking left/up) to 1 (looking right/down).
        """
        # Eye width
        eye_width = np.sqrt(
            (outer_corner[0] - inner_corner[0])**2 +
            (outer_corner[1] - inner_corner[1])**2
        )
        
        if eye_width < 1:
            return (0.0, 0.0)
        
        # Eye center
        eye_center_x = (inner_corner[0] + outer_corner[0]) / 2
        eye_center_y = (inner_corner[1] + outer_corner[1]) / 2
        
        # Normalized position (-1 to 1)
        gaze_x = (iris[0] - eye_center_x) / (eye_width / 2)
        gaze_y = (iris[1] - eye_center_y) / (eye_width / 4)  # Less vertical range
        
        # Clamp to [-1, 1]
        gaze_x = max(-1, min(1, gaze_x))
        gaze_y = max(-1, min(1, gaze_y))
        
        return (gaze_x, gaze_y)
    
    def analyze(self, duration: Optional[float] = None) -> GazeAnalysis:
        """
        Analyze gaze patterns from collected history.
        
        Args:
            duration: Total video duration (uses history if not provided)
            
        Returns:
            GazeAnalysis with detailed metrics
        """
        if not self.gaze_history:
            return GazeAnalysis(
                eye_contact_percentage=0.0,
                average_contact_duration=0.0,
                gaze_stability=0.0,
                looking_away_events=[],
                heat_map_data=None,
                assessment="insufficient_data",
                recommendations=["Unable to analyze - no face detected"]
            )
        
        total_duration = duration or (
            self.gaze_history[-1].timestamp - self.gaze_history[0].timestamp
        )
        
        if total_duration <= 0:
            total_duration = 1.0
        
        # Calculate eye contact percentage
        contact_frames = sum(1 for g in self.gaze_history if g.looking_at_camera)
        eye_contact_percentage = (contact_frames / len(self.gaze_history)) * 100
        
        # Find looking away events
        looking_away_events = self._find_looking_away_events()
        
        # Calculate average contact duration
        contact_durations = self._calculate_contact_durations()
        avg_contact_duration = np.mean(contact_durations) if contact_durations else 0.0
        
        # Calculate gaze stability
        gaze_stability = self._calculate_stability()
        
        # Create heat map data
        heat_map_data = self._create_heat_map()
        
        # Generate assessment
        assessment, recommendations = self._generate_assessment(
            eye_contact_percentage,
            gaze_stability,
            looking_away_events
        )
        
        return GazeAnalysis(
            eye_contact_percentage=float(eye_contact_percentage),
            average_contact_duration=float(avg_contact_duration),
            gaze_stability=float(gaze_stability),
            looking_away_events=looking_away_events,
            heat_map_data=heat_map_data,
            assessment=assessment,
            recommendations=recommendations
        )
    
    def _find_looking_away_events(self) -> List[Dict]:
        """Find periods where user looked away from camera"""
        events = []
        event_start = None
        
        for i, gaze in enumerate(self.gaze_history):
            if not gaze.looking_at_camera and gaze.confidence > 0:
                if event_start is None:
                    event_start = i
            else:
                if event_start is not None:
                    start_time = self.gaze_history[event_start].timestamp
                    end_time = self.gaze_history[i - 1].timestamp
                    duration = end_time - start_time
                    
                    if duration > 0.5:  # Only track significant events
                        # Determine direction
                        gaze_directions = [
                            self.gaze_history[j].gaze_direction
                            for j in range(event_start, i)
                            if self.gaze_history[j].confidence > 0
                        ]
                        if gaze_directions:
                            avg_x = np.mean([g[0] for g in gaze_directions])
                            avg_y = np.mean([g[1] for g in gaze_directions])
                            direction = self._get_direction_label(avg_x, avg_y)
                        else:
                            direction = "unknown"
                        
                        events.append({
                            "start": start_time,
                            "end": end_time,
                            "duration": duration,
                            "direction": direction
                        })
                    
                    event_start = None
        
        return events
    
    def _get_direction_label(self, gaze_x: float, gaze_y: float) -> str:
        """Get human-readable direction label"""
        if abs(gaze_x) > abs(gaze_y):
            return "left" if gaze_x < 0 else "right"
        else:
            return "up" if gaze_y < 0 else "down"
    
    def _calculate_contact_durations(self) -> List[float]:
        """Calculate durations of continuous eye contact"""
        durations = []
        contact_start = None
        
        for gaze in self.gaze_history:
            if gaze.looking_at_camera:
                if contact_start is None:
                    contact_start = gaze.timestamp
            else:
                if contact_start is not None:
                    duration = gaze.timestamp - contact_start
                    if duration > 0:
                        durations.append(duration)
                    contact_start = None
        
        return durations
    
    def _calculate_stability(self) -> float:
        """Calculate gaze stability (inverse of variance)"""
        if len(self.gaze_history) < 2:
            return 0.5
        
        gaze_x = [g.gaze_direction[0] for g in self.gaze_history if g.confidence > 0]
        gaze_y = [g.gaze_direction[1] for g in self.gaze_history if g.confidence > 0]
        
        if len(gaze_x) < 2:
            return 0.5
        
        variance_x = np.var(gaze_x)
        variance_y = np.var(gaze_y)
        total_variance = variance_x + variance_y
        
        # Convert to stability score (0-1, higher = more stable)
        stability = 1.0 / (1.0 + total_variance * 5)
        return float(stability)
    
    def _create_heat_map(self, resolution: int = 20) -> np.ndarray:
        """Create heat map of gaze positions"""
        heat_map = np.zeros((resolution, resolution))
        
        for gaze in self.gaze_history:
            if gaze.confidence > 0:
                # Map from [-1, 1] to [0, resolution-1]
                x = int((gaze.gaze_direction[0] + 1) / 2 * (resolution - 1))
                y = int((gaze.gaze_direction[1] + 1) / 2 * (resolution - 1))
                
                x = max(0, min(resolution - 1, x))
                y = max(0, min(resolution - 1, y))
                
                heat_map[y, x] += 1
        
        # Normalize
        if heat_map.max() > 0:
            heat_map = heat_map / heat_map.max()
        
        return heat_map
    
    def _generate_assessment(
        self,
        eye_contact_pct: float,
        stability: float,
        looking_away_events: List[Dict]
    ) -> Tuple[str, List[str]]:
        """Generate assessment and recommendations"""
        recommendations = []
        
        if eye_contact_pct >= 70:
            assessment = "excellent"
        elif eye_contact_pct >= 50:
            assessment = "good"
        elif eye_contact_pct >= 30:
            assessment = "needs_improvement"
        else:
            assessment = "poor"
        
        # Generate recommendations
        if eye_contact_pct < 50:
            recommendations.append(
                "Try to maintain more consistent eye contact with the camera. "
                "Aim for at least 60-70% eye contact during interviews."
            )
        
        if stability < 0.5:
            recommendations.append(
                "Your gaze appears unstable. Practice focusing on a single point "
                "(the camera lens) when speaking to project confidence."
            )
        
        # Analyze looking away patterns
        long_breaks = [e for e in looking_away_events if e["duration"] > 3]
        if long_breaks:
            recommendations.append(
                f"You had {len(long_breaks)} instances of looking away for more than 3 seconds. "
                "Brief glances away are natural, but extended breaks may signal disengagement."
            )
        
        down_looks = [e for e in looking_away_events if e["direction"] == "down"]
        if len(down_looks) > 3:
            recommendations.append(
                "You frequently look downward, which might convey uncertainty. "
                "If you're reading notes, try to minimize this."
            )
        
        if assessment == "excellent" and not recommendations:
            recommendations.append(
                "Excellent eye contact! You maintained consistent engagement with the camera."
            )
        
        return assessment, recommendations
    
    def reset(self):
        """Reset gaze history"""
        self.gaze_history = []
        self.start_time = None
    
    def close(self):
        """Release resources"""
        self.face_mesh.close()


def track_gaze(landmarks: Dict) -> Dict:
    """
    Legacy compatibility function - track gaze from landmarks.
    
    Args:
        landmarks: Dictionary with 'landmarks' array
        
    Returns:
        Gaze direction and eye contact status
    """
    if not landmarks.get("detected", False):
        return {
            "gaze_direction": [0.0, 0.0],
            "looking_at_camera": False,
            "confidence": 0.0
        }
    
    # Simplified gaze calculation from landmarks array
    lm = np.array(landmarks.get("landmarks", []))
    if len(lm) < 478:
        return {
            "gaze_direction": [0.0, 0.0],
            "looking_at_camera": False,
            "confidence": 0.0
        }
    
    # Use iris positions
    left_iris = np.mean(lm[LEFT_IRIS], axis=0) if len(lm) > 472 else lm[33]
    right_iris = np.mean(lm[RIGHT_IRIS], axis=0) if len(lm) > 477 else lm[263]
    
    # Eye centers
    left_center = (lm[LEFT_EYE_INNER] + lm[LEFT_EYE_OUTER]) / 2
    right_center = (lm[RIGHT_EYE_INNER] + lm[RIGHT_EYE_OUTER]) / 2
    
    # Calculate offset
    left_offset = left_iris[:2] - left_center[:2]
    right_offset = right_iris[:2] - right_center[:2]
    
    avg_offset = (left_offset + right_offset) / 2
    
    # Normalize
    gaze_x = float(avg_offset[0] / 20)  # Approximate normalization
    gaze_y = float(avg_offset[1] / 20)
    
    distance = np.sqrt(gaze_x**2 + gaze_y**2)
    looking_at_camera = distance < 0.15
    
    return {
        "gaze_direction": [gaze_x, gaze_y],
        "looking_at_camera": looking_at_camera,
        "confidence": 0.9
    }


def analyze_eye_contact(gaze_history: List[Dict], duration: float) -> Dict:
    """
    Legacy compatibility function - analyze eye contact patterns.
    
    Args:
        gaze_history: History of gaze tracking results
        duration: Total video duration
        
    Returns:
        Eye contact analysis
    """
    if not gaze_history:
        return {
            "eye_contact_percentage": 0.0,
            "average_contact_duration": 0.0,
            "assessment": "insufficient_data",
            "recommendations": ["No gaze data available"]
        }
    
    contact_count = sum(1 for g in gaze_history if g.get("looking_at_camera", False))
    eye_contact_pct = (contact_count / len(gaze_history)) * 100
    
    if eye_contact_pct >= 70:
        assessment = "excellent"
    elif eye_contact_pct >= 50:
        assessment = "good"
    elif eye_contact_pct >= 30:
        assessment = "needs_improvement"
    else:
        assessment = "poor"
    
    recommendations = []
    if eye_contact_pct < 60:
        recommendations.append("Practice maintaining eye contact with the camera")
    else:
        recommendations.append("Good eye contact maintained")
    
    return {
        "eye_contact_percentage": float(eye_contact_pct),
        "average_contact_duration": duration / max(1, contact_count),
        "assessment": assessment,
        "recommendations": recommendations
    }
