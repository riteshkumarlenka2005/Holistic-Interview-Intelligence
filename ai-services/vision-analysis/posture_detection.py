"""
Posture Detection Module
Analyzes body posture and movements using MediaPipe Pose
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


# MediaPipe Pose landmark indices
POSE_LANDMARKS = {
    "nose": 0,
    "left_eye_inner": 1,
    "left_eye": 2,
    "left_eye_outer": 3,
    "right_eye_inner": 4,
    "right_eye": 5,
    "right_eye_outer": 6,
    "left_ear": 7,
    "right_ear": 8,
    "mouth_left": 9,
    "mouth_right": 10,
    "left_shoulder": 11,
    "right_shoulder": 12,
    "left_elbow": 13,
    "right_elbow": 14,
    "left_wrist": 15,
    "right_wrist": 16,
    "left_pinky": 17,
    "right_pinky": 18,
    "left_index": 19,
    "right_index": 20,
    "left_thumb": 21,
    "right_thumb": 22,
    "left_hip": 23,
    "right_hip": 24,
}


@dataclass
class PosturePoint:
    """Single posture measurement"""
    timestamp: float
    posture_type: str  # upright, slouching, leaning_left, leaning_right, leaning_forward
    shoulder_alignment: float  # -1 to 1, 0 is level
    head_position: Tuple[float, float]  # relative to shoulders
    confidence: float
    body_landmarks: Optional[np.ndarray]


@dataclass
class HandMovement:
    """Hand movement metrics"""
    left_hand_position: Tuple[float, float]
    right_hand_position: Tuple[float, float]
    left_movement_amplitude: float
    right_movement_amplitude: float
    gesture_frequency: float  # gestures per minute
    assessment: str  # controlled, expressive, nervous


@dataclass
class PostureAnalysis:
    """Complete posture analysis results"""
    dominant_posture: str
    average_shoulder_alignment: float
    posture_stability: float  # 0-1
    posture_changes: int
    hand_movement: HandMovement
    engagement_score: float
    recommendations: List[str]


class PostureDetector:
    """
    MediaPipe Pose-based posture detection.
    Analyzes body posture, shoulder alignment, and hand movements.
    """
    
    # Thresholds
    SLOUCH_THRESHOLD = -0.1  # Head below shoulder line
    LEAN_THRESHOLD = 0.08  # Shoulder tilt threshold
    
    def __init__(
        self,
        static_image_mode: bool = False,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5
    ):
        """
        Initialize posture detector.
        
        Args:
            static_image_mode: If True, treats each image independently
            min_detection_confidence: Minimum detection confidence
            min_tracking_confidence: Minimum tracking confidence
        """
        _load_dependencies()
        
        self.mp_pose = mp.solutions.pose
        self.pose = self.mp_pose.Pose(
            static_image_mode=static_image_mode,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.posture_history: List[PosturePoint] = []
        self.hand_positions_left: List[Tuple[float, float]] = []
        self.hand_positions_right: List[Tuple[float, float]] = []
        self.start_time: Optional[float] = None
    
    def process_frame(
        self,
        frame: np.ndarray,
        timestamp: Optional[float] = None
    ) -> PosturePoint:
        """
        Process a single frame for posture detection.
        
        Args:
            frame: BGR image frame
            timestamp: Optional timestamp
            
        Returns:
            PosturePoint with current posture info
        """
        if self.start_time is None:
            self.start_time = time.time()
        
        ts = timestamp if timestamp is not None else time.time() - self.start_time
        
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame.shape[:2]
        
        # Process frame
        results = self.pose.process(rgb_frame)
        
        if not results.pose_landmarks:
            posture = PosturePoint(
                timestamp=ts,
                posture_type="unknown",
                shoulder_alignment=0.0,
                head_position=(0.0, 0.0),
                confidence=0.0,
                body_landmarks=None
            )
            self.posture_history.append(posture)
            return posture
        
        # Extract landmarks
        landmarks = np.array([
            [lm.x, lm.y, lm.z, lm.visibility]
            for lm in results.pose_landmarks.landmark
        ])
        
        # Get key points
        left_shoulder = landmarks[POSE_LANDMARKS["left_shoulder"]]
        right_shoulder = landmarks[POSE_LANDMARKS["right_shoulder"]]
        nose = landmarks[POSE_LANDMARKS["nose"]]
        left_wrist = landmarks[POSE_LANDMARKS["left_wrist"]]
        right_wrist = landmarks[POSE_LANDMARKS["right_wrist"]]
        
        # Calculate shoulder alignment (-1 to 1, 0 is level)
        shoulder_diff = left_shoulder[1] - right_shoulder[1]  # Y difference
        shoulder_width = abs(left_shoulder[0] - right_shoulder[0])
        shoulder_alignment = shoulder_diff / shoulder_width if shoulder_width > 0 else 0
        
        # Calculate head position relative to shoulders
        shoulder_center_x = (left_shoulder[0] + right_shoulder[0]) / 2
        shoulder_center_y = (left_shoulder[1] + right_shoulder[1]) / 2
        head_offset_x = nose[0] - shoulder_center_x
        head_offset_y = nose[1] - shoulder_center_y
        
        # Determine posture type
        posture_type = self._classify_posture(
            shoulder_alignment,
            head_offset_x,
            head_offset_y
        )
        
        # Track hand positions
        self.hand_positions_left.append((left_wrist[0], left_wrist[1]))
        self.hand_positions_right.append((right_wrist[0], right_wrist[1]))
        
        # Calculate confidence
        visibility = np.mean([
            left_shoulder[3], right_shoulder[3],
            nose[3], left_wrist[3], right_wrist[3]
        ])
        
        posture = PosturePoint(
            timestamp=ts,
            posture_type=posture_type,
            shoulder_alignment=float(shoulder_alignment),
            head_position=(float(head_offset_x), float(head_offset_y)),
            confidence=float(visibility),
            body_landmarks=landmarks
        )
        
        self.posture_history.append(posture)
        return posture
    
    def _classify_posture(
        self,
        shoulder_alignment: float,
        head_offset_x: float,
        head_offset_y: float
    ) -> str:
        """Classify posture based on measurements"""
        # Check for leaning
        if shoulder_alignment > self.LEAN_THRESHOLD:
            return "leaning_left"
        elif shoulder_alignment < -self.LEAN_THRESHOLD:
            return "leaning_right"
        
        # Check for forward lean (head forward of shoulders in z)
        if head_offset_y < self.SLOUCH_THRESHOLD:
            return "slouching"
        
        # Check for lateral head offset
        if abs(head_offset_x) > 0.1:
            return "leaning_forward"
        
        return "upright"
    
    def analyze_hand_movements(self, duration: float) -> HandMovement:
        """Analyze hand movement patterns"""
        if not self.hand_positions_left or not self.hand_positions_right:
            return HandMovement(
                left_hand_position=(0.0, 0.0),
                right_hand_position=(0.0, 0.0),
                left_movement_amplitude=0.0,
                right_movement_amplitude=0.0,
                gesture_frequency=0.0,
                assessment="unknown"
            )
        
        # Current positions
        left_pos = self.hand_positions_left[-1]
        right_pos = self.hand_positions_right[-1]
        
        # Calculate movement amplitudes
        left_positions = np.array(self.hand_positions_left)
        right_positions = np.array(self.hand_positions_right)
        
        left_amplitude = float(np.std(left_positions[:, 0]) + np.std(left_positions[:, 1]))
        right_amplitude = float(np.std(right_positions[:, 0]) + np.std(right_positions[:, 1]))
        
        # Estimate gesture frequency (significant position changes)
        left_changes = self._count_significant_changes(left_positions)
        right_changes = self._count_significant_changes(right_positions)
        total_changes = left_changes + right_changes
        
        gesture_frequency = (total_changes / duration) * 60 if duration > 0 else 0
        
        # Assess movement pattern
        total_amplitude = left_amplitude + right_amplitude
        if total_amplitude < 0.05:
            assessment = "minimal"
        elif total_amplitude < 0.15:
            assessment = "controlled"
        elif total_amplitude < 0.3:
            assessment = "expressive"
        else:
            if gesture_frequency > 30:
                assessment = "nervous"
            else:
                assessment = "very_expressive"
        
        return HandMovement(
            left_hand_position=left_pos,
            right_hand_position=right_pos,
            left_movement_amplitude=left_amplitude,
            right_movement_amplitude=right_amplitude,
            gesture_frequency=float(gesture_frequency),
            assessment=assessment
        )
    
    def _count_significant_changes(
        self,
        positions: np.ndarray,
        threshold: float = 0.05
    ) -> int:
        """Count significant position changes"""
        if len(positions) < 2:
            return 0
        
        changes = 0
        for i in range(1, len(positions)):
            dist = np.linalg.norm(positions[i] - positions[i - 1])
            if dist > threshold:
                changes += 1
        
        return changes
    
    def analyze(self, duration: Optional[float] = None) -> PostureAnalysis:
        """
        Analyze posture patterns from collected history.
        
        Args:
            duration: Total duration (computed from history if not provided)
            
        Returns:
            PostureAnalysis with detailed metrics
        """
        if not self.posture_history:
            return PostureAnalysis(
                dominant_posture="unknown",
                average_shoulder_alignment=0.0,
                posture_stability=0.0,
                posture_changes=0,
                hand_movement=HandMovement(
                    (0, 0), (0, 0), 0, 0, 0, "unknown"
                ),
                engagement_score=0.0,
                recommendations=["No posture data available"]
            )
        
        total_duration = duration or (
            self.posture_history[-1].timestamp - self.posture_history[0].timestamp
        )
        if total_duration <= 0:
            total_duration = 1.0
        
        # Find dominant posture
        posture_counts = {}
        for p in self.posture_history:
            if p.posture_type != "unknown":
                posture_counts[p.posture_type] = posture_counts.get(p.posture_type, 0) + 1
        
        dominant_posture = max(posture_counts.keys(), key=lambda k: posture_counts[k]) if posture_counts else "unknown"
        
        # Calculate average shoulder alignment
        alignments = [p.shoulder_alignment for p in self.posture_history if p.confidence > 0]
        avg_alignment = float(np.mean(alignments)) if alignments else 0.0
        
        # Calculate stability
        posture_types = [p.posture_type for p in self.posture_history if p.confidence > 0]
        posture_changes = sum(
            1 for i in range(1, len(posture_types))
            if posture_types[i] != posture_types[i - 1]
        )
        stability = 1.0 / (1.0 + posture_changes / max(1, len(posture_types)) * 10)
        
        # Analyze hand movements
        hand_movement = self.analyze_hand_movements(total_duration)
        
        # Calculate engagement score
        engagement = self._calculate_engagement(
            dominant_posture, stability, hand_movement
        )
        
        # Generate recommendations
        recommendations = self._generate_recommendations(
            dominant_posture,
            avg_alignment,
            stability,
            hand_movement
        )
        
        return PostureAnalysis(
            dominant_posture=dominant_posture,
            average_shoulder_alignment=avg_alignment,
            posture_stability=float(stability),
            posture_changes=posture_changes,
            hand_movement=hand_movement,
            engagement_score=float(engagement),
            recommendations=recommendations
        )
    
    def _calculate_engagement(
        self,
        posture: str,
        stability: float,
        hand_movement: HandMovement
    ) -> float:
        """Calculate engagement score from posture metrics"""
        scores = []
        
        # Posture score
        posture_scores = {
            "upright": 0.9,
            "leaning_forward": 0.8,  # Could indicate interest
            "slouching": 0.4,
            "leaning_left": 0.5,
            "leaning_right": 0.5,
            "unknown": 0.3
        }
        scores.append(posture_scores.get(posture, 0.5))
        
        # Stability contributes positively
        scores.append(0.5 + stability * 0.5)
        
        # Hand movement
        movement_scores = {
            "expressive": 0.85,
            "controlled": 0.8,
            "minimal": 0.5,
            "nervous": 0.4,
            "very_expressive": 0.7,
            "unknown": 0.5
        }
        scores.append(movement_scores.get(hand_movement.assessment, 0.5))
        
        return np.mean(scores)
    
    def _generate_recommendations(
        self,
        posture: str,
        alignment: float,
        stability: float,
        hand_movement: HandMovement
    ) -> List[str]:
        """Generate posture recommendations"""
        recommendations = []
        
        if posture == "slouching":
            recommendations.append(
                "Sit up straight with your shoulders back. Position your camera at eye level "
                "to encourage better posture."
            )
        
        if posture in ["leaning_left", "leaning_right"]:
            recommendations.append(
                "Try to keep your shoulders level. Leaning to one side can appear unbalanced "
                "or distracted."
            )
        
        if abs(alignment) > 0.1:
            recommendations.append(
                "Keep your shoulders level and centered in the frame for a more professional appearance."
            )
        
        if stability < 0.5:
            recommendations.append(
                "Your posture changes frequently, which might indicate restlessness. "
                "Try to maintain a steady, confident position."
            )
        
        if hand_movement.assessment == "nervous":
            recommendations.append(
                "Your hand movements appear rapid or fidgety. Try keeping your hands "
                "visible but calm, perhaps resting on the desk."
            )
        elif hand_movement.assessment == "minimal":
            recommendations.append(
                "Consider using more hand gestures to emphasize key points. "
                "Natural gestures make you appear more engaging."
            )
        
        if not recommendations:
            recommendations.append(
                "Great posture! You appear confident and engaged. Keep your current body language."
            )
        
        return recommendations
    
    def reset(self):
        """Reset history"""
        self.posture_history = []
        self.hand_positions_left = []
        self.hand_positions_right = []
        self.start_time = None
    
    def close(self):
        """Release resources"""
        self.pose.close()


def detect_posture(frame: np.ndarray) -> Dict:
    """
    Convenience function to detect posture in a single frame.
    
    Args:
        frame: BGR image frame
        
    Returns:
        Posture detection results
    """
    detector = PostureDetector(static_image_mode=True)
    result = detector.process_frame(frame)
    detector.close()
    
    return {
        "detected": result.confidence > 0,
        "posture_type": result.posture_type,
        "confidence": result.confidence,
        "shoulder_alignment": result.shoulder_alignment,
        "body_landmarks": result.body_landmarks.tolist() if result.body_landmarks is not None else []
    }


def analyze_posture_over_time(posture_history: List[Dict]) -> Dict:
    """
    Legacy compatibility function.
    
    Args:
        posture_history: List of posture detection results
        
    Returns:
        Posture analysis summary
    """
    if not posture_history:
        return {
            "average_posture": "unknown",
            "posture_changes": 0,
            "stability_score": 0.0,
            "assessment": "insufficient_data",
            "recommendations": ["No posture data available"]
        }
    
    # Count posture types
    posture_counts = {}
    for p in posture_history:
        ptype = p.get("posture_type", "unknown")
        posture_counts[ptype] = posture_counts.get(ptype, 0) + 1
    
    avg_posture = max(posture_counts.keys(), key=lambda k: posture_counts[k])
    
    # Count changes
    types = [p.get("posture_type", "unknown") for p in posture_history]
    changes = sum(1 for i in range(1, len(types)) if types[i] != types[i - 1])
    
    stability = 1.0 - min(1.0, changes / max(1, len(types)) * 5)
    
    assessment = "good" if avg_posture == "upright" and stability > 0.6 else "needs_improvement"
    
    recommendations = []
    if avg_posture != "upright":
        recommendations.append("Work on maintaining an upright posture")
    if stability < 0.6:
        recommendations.append("Try to minimize unnecessary movement")
    if not recommendations:
        recommendations.append("Good posture maintained throughout")
    
    return {
        "average_posture": avg_posture,
        "posture_changes": changes,
        "stability_score": stability,
        "assessment": assessment,
        "recommendations": recommendations
    }
