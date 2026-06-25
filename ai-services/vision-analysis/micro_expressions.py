"""
Micro-expressions Detection Module
Detects subtle facial expressions that may reveal true emotions
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
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


class Expression(Enum):
    """Basic expression categories"""
    NEUTRAL = "neutral"
    HAPPY = "happy"
    SAD = "sad"
    ANGRY = "angry"
    SURPRISED = "surprised"
    FEARFUL = "fearful"
    DISGUSTED = "disgusted"
    CONTEMPT = "contempt"


EXPRESSION_TYPES = [e.value for e in Expression]


# Action Units based on Facial Action Coding System (FACS)
# Simplified set for interview analysis
ACTION_UNITS = {
    "AU1": "inner_brow_raise",    # Surprise, sadness
    "AU2": "outer_brow_raise",    # Surprise
    "AU4": "brow_lower",          # Anger, confusion
    "AU5": "upper_lid_raise",     # Surprise, fear
    "AU6": "cheek_raise",         # Genuine smile
    "AU7": "lid_tighten",         # Anger
    "AU9": "nose_wrinkle",        # Disgust
    "AU10": "upper_lip_raise",    # Disgust
    "AU12": "lip_corner_pull",    # Smile
    "AU14": "dimpler",            # Contempt
    "AU15": "lip_corner_depress", # Sadness
    "AU17": "chin_raise",         # Doubt, contempt
    "AU20": "lip_stretch",        # Fear
    "AU23": "lip_tighten",        # Anger
    "AU24": "lip_press",          # Tension
    "AU25": "lips_part",          # Surprise
    "AU26": "jaw_drop",           # Surprise
}


@dataclass
class MicroExpression:
    """Detected micro-expression"""
    timestamp: float
    expression: str
    intensity: float  # 0-1
    confidence: float
    duration_ms: float
    action_units: Dict[str, float]


@dataclass
class ExpressionState:
    """Current expression state"""
    dominant_expression: str
    expression_scores: Dict[str, float]
    action_units: Dict[str, float]
    emotional_valence: float  # -1 (negative) to 1 (positive)
    arousal: float  # 0 (calm) to 1 (excited)


@dataclass
class ExpressionAnalysis:
    """Complete expression analysis results"""
    micro_expressions: List[MicroExpression]
    expression_distribution: Dict[str, float]
    dominant_expression: str
    emotional_congruence: float  # How consistent expressions are with speech
    authentic_smile_count: int
    stress_indicators: int
    assessment: str
    recommendations: List[str]


class MicroExpressionDetector:
    """
    Detects micro-expressions and emotional states from facial landmarks.
    Uses facial geometry and Action Units (simplified FACS).
    """
    
    # Thresholds for micro-expression detection
    MIN_INTENSITY_CHANGE = 0.15
    MAX_DURATION_MS = 500  # Micro-expressions last < 500ms
    MIN_DURATION_MS = 50
    
    def __init__(
        self,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5
    ):
        """
        Initialize micro-expression detector.
        
        Args:
            min_detection_confidence: Minimum face detection confidence
            min_tracking_confidence: Minimum tracking confidence
        """
        _load_dependencies()
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            max_num_faces=1,
            refine_landmarks=True,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        
        self.expression_history: List[ExpressionState] = []
        self.micro_expressions: List[MicroExpression] = []
        self.prev_landmarks: Optional[np.ndarray] = None
        self.prev_timestamp: Optional[float] = None
        self.start_time: Optional[float] = None
    
    def process_frame(
        self,
        frame: np.ndarray,
        timestamp: Optional[float] = None
    ) -> ExpressionState:
        """
        Process a frame for expression detection.
        
        Args:
            frame: BGR image frame
            timestamp: Optional timestamp
            
        Returns:
            Current ExpressionState
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
            state = ExpressionState(
                dominant_expression="unknown",
                expression_scores={e: 0.0 for e in EXPRESSION_TYPES},
                action_units={},
                emotional_valence=0.0,
                arousal=0.0
            )
            return state
        
        # Extract landmarks
        landmarks = np.array([
            [lm.x * w, lm.y * h, lm.z * w]
            for lm in results.multi_face_landmarks[0].landmark
        ])
        
        # Calculate action units
        action_units = self._calculate_action_units(landmarks)
        
        # Estimate expression from action units
        expression_scores = self._estimate_expressions(action_units)
        
        # Find dominant expression
        dominant = max(expression_scores.keys(), key=lambda k: expression_scores[k])
        
        # Calculate valence and arousal
        valence = self._calculate_valence(expression_scores)
        arousal = self._calculate_arousal(action_units)
        
        state = ExpressionState(
            dominant_expression=dominant,
            expression_scores=expression_scores,
            action_units=action_units,
            emotional_valence=valence,
            arousal=arousal
        )
        
        # Detect micro-expressions (rapid changes)
        if self.prev_landmarks is not None and self.prev_timestamp is not None:
            self._detect_micro_expression(
                landmarks, self.prev_landmarks,
                ts, self.prev_timestamp,
                action_units
            )
        
        self.prev_landmarks = landmarks
        self.prev_timestamp = ts
        self.expression_history.append(state)
        
        return state
    
    def _calculate_action_units(self, landmarks: np.ndarray) -> Dict[str, float]:
        """Calculate simplified Action Unit activations from landmarks"""
        aus = {}
        
        # Get key landmarks
        left_brow_inner = landmarks[107]
        left_brow_outer = landmarks[70]
        right_brow_inner = landmarks[336]
        right_brow_outer = landmarks[300]
        
        left_eye_top = landmarks[159]
        left_eye_bottom = landmarks[145]
        right_eye_top = landmarks[386]
        right_eye_bottom = landmarks[374]
        
        nose_tip = landmarks[1]
        nose_bridge = landmarks[6]
        
        upper_lip = landmarks[13]
        lower_lip = landmarks[14]
        left_mouth_corner = landmarks[61]
        right_mouth_corner = landmarks[291]
        mouth_top = landmarks[0]
        mouth_bottom = landmarks[17]
        
        left_cheek = landmarks[50]
        right_cheek = landmarks[280]
        
        # Reference distances
        face_height = np.linalg.norm(landmarks[10] - landmarks[152])
        face_width = np.linalg.norm(landmarks[234] - landmarks[454])
        
        if face_height == 0 or face_width == 0:
            return {au: 0.0 for au in ACTION_UNITS}
        
        # AU1 - Inner brow raise
        brow_height = (left_brow_inner[1] + right_brow_inner[1]) / 2
        eye_height = (left_eye_top[1] + right_eye_top[1]) / 2
        aus["AU1"] = max(0, min(1, (eye_height - brow_height) / face_height * 10))
        
        # AU2 - Outer brow raise
        outer_brow_height = (left_brow_outer[1] + right_brow_outer[1]) / 2
        aus["AU2"] = max(0, min(1, (eye_height - outer_brow_height) / face_height * 10))
        
        # AU4 - Brow lower (inverse of raise)
        aus["AU4"] = max(0, 1 - aus["AU1"])
        
        # AU5 - Upper lid raise
        left_eye_open = left_eye_bottom[1] - left_eye_top[1]
        right_eye_open = right_eye_bottom[1] - right_eye_top[1]
        eye_openness = (left_eye_open + right_eye_open) / 2
        aus["AU5"] = max(0, min(1, eye_openness / face_height * 15))
        
        # AU6 - Cheek raise
        cheek_height = (left_cheek[1] + right_cheek[1]) / 2
        mouth_height = (left_mouth_corner[1] + right_mouth_corner[1]) / 2
        aus["AU6"] = max(0, min(1, (mouth_height - cheek_height) / face_height * 5))
        
        # AU12 - Lip corner pull (smile)
        mouth_width = np.linalg.norm(left_mouth_corner - right_mouth_corner)
        aus["AU12"] = max(0, min(1, mouth_width / face_width * 2 - 0.3))
        
        # AU14 - Dimpler (asymmetric, detected as difference)
        left_corner_height = left_mouth_corner[1]
        right_corner_height = right_mouth_corner[1]
        corner_diff = abs(left_corner_height - right_corner_height)
        aus["AU14"] = max(0, min(1, corner_diff / face_height * 20))
        
        # AU15 - Lip corner depress (frown)
        mouth_center_y = (upper_lip[1] + lower_lip[1]) / 2
        corner_avg_y = (left_mouth_corner[1] + right_mouth_corner[1]) / 2
        aus["AU15"] = max(0, min(1, (corner_avg_y - mouth_center_y) / face_height * 10))
        
        # AU25 - Lips part
        lip_distance = np.linalg.norm(upper_lip - lower_lip)
        aus["AU25"] = max(0, min(1, lip_distance / face_height * 8))
        
        # AU26 - Jaw drop
        jaw_open = mouth_bottom[1] - mouth_top[1]
        aus["AU26"] = max(0, min(1, jaw_open / face_height * 5))
        
        # Fill remaining AUs with estimates
        aus["AU7"] = max(0, 1 - aus["AU5"])  # Lid tighten (inverse of raise)
        aus["AU9"] = 0.0  # Nose wrinkle - hard to detect from landmarks
        aus["AU10"] = aus["AU9"]  # Correlates with disgust
        aus["AU17"] = 0.0  # Chin raise
        aus["AU20"] = max(0, aus["AU25"] * aus["AU4"])  # Fear stretch
        aus["AU23"] = max(0, 1 - aus["AU25"] - aus["AU12"])  # Lip tighten
        aus["AU24"] = aus["AU23"]  # Lip press
        
        return aus
    
    def _estimate_expressions(self, aus: Dict[str, float]) -> Dict[str, float]:
        """Estimate expression probabilities from action units"""
        scores = {}
        
        # Neutral - low activation overall
        total_activation = sum(aus.values()) / len(aus)
        scores["neutral"] = max(0, 1 - total_activation * 2)
        
        # Happy - AU6 (cheek raise) + AU12 (lip corner pull)
        scores["happy"] = min(1, (aus.get("AU6", 0) + aus.get("AU12", 0)) / 1.5)
        
        # Sad - AU1 + AU15 (inner brow + lip corner depress)
        scores["sad"] = min(1, (aus.get("AU1", 0) * 0.5 + aus.get("AU15", 0)) / 1.2)
        
        # Angry - AU4 + AU7 + AU23 (brow lower + lid tighten + lip tighten)
        scores["angry"] = min(1, (aus.get("AU4", 0) + aus.get("AU7", 0) + aus.get("AU23", 0)) / 2)
        
        # Surprised - AU1 + AU2 + AU5 + AU26 (brows + eyes + jaw)
        scores["surprised"] = min(1, (
            aus.get("AU1", 0) + aus.get("AU2", 0) + 
            aus.get("AU5", 0) + aus.get("AU26", 0)
        ) / 3)
        
        # Fearful - AU1 + AU2 + AU4 + AU5 + AU20
        scores["fearful"] = min(1, (
            aus.get("AU1", 0) + aus.get("AU4", 0) + 
            aus.get("AU5", 0) + aus.get("AU20", 0)
        ) / 3)
        
        # Disgusted - AU9 + AU10 (nose wrinkle + upper lip raise)
        scores["disgusted"] = min(1, (aus.get("AU9", 0) + aus.get("AU10", 0)) / 1.5)
        
        # Contempt - AU14 (asymmetric lip corner)
        scores["contempt"] = aus.get("AU14", 0)
        
        # Normalize
        total = sum(scores.values())
        if total > 0:
            scores = {k: v / total for k, v in scores.items()}
        
        return scores
    
    def _calculate_valence(self, expression_scores: Dict[str, float]) -> float:
        """Calculate emotional valence (positive/negative)"""
        positive = expression_scores.get("happy", 0) + expression_scores.get("surprised", 0) * 0.3
        negative = (
            expression_scores.get("sad", 0) +
            expression_scores.get("angry", 0) +
            expression_scores.get("fearful", 0) +
            expression_scores.get("disgusted", 0) +
            expression_scores.get("contempt", 0)
        )
        return positive - negative
    
    def _calculate_arousal(self, aus: Dict[str, float]) -> float:
        """Calculate emotional arousal (excitement level)"""
        high_arousal_aus = ["AU1", "AU2", "AU5", "AU25", "AU26"]
        arousal = sum(aus.get(au, 0) for au in high_arousal_aus) / len(high_arousal_aus)
        return min(1, arousal)
    
    def _detect_micro_expression(
        self,
        current_landmarks: np.ndarray,
        prev_landmarks: np.ndarray,
        current_ts: float,
        prev_ts: float,
        action_units: Dict[str, float]
    ):
        """Detect rapid micro-expressions from landmark changes"""
        duration_ms = (current_ts - prev_ts) * 1000
        
        if duration_ms < self.MIN_DURATION_MS or duration_ms > self.MAX_DURATION_MS * 2:
            return
        
        # Calculate movement intensity
        movement = np.linalg.norm(current_landmarks - prev_landmarks, axis=1)
        avg_movement = np.mean(movement)
        
        # Normalize by face size
        face_size = np.linalg.norm(
            current_landmarks[10] - current_landmarks[152]
        )
        if face_size > 0:
            normalized_movement = avg_movement / face_size
        else:
            normalized_movement = 0
        
        # Check if movement indicates micro-expression
        if normalized_movement > self.MIN_INTENSITY_CHANGE:
            # Determine expression type
            expression_scores = self._estimate_expressions(action_units)
            dominant = max(expression_scores.keys(), key=lambda k: expression_scores[k])
            
            if dominant != "neutral" and expression_scores[dominant] > 0.3:
                me = MicroExpression(
                    timestamp=current_ts,
                    expression=dominant,
                    intensity=float(normalized_movement),
                    confidence=expression_scores[dominant],
                    duration_ms=duration_ms,
                    action_units=action_units.copy()
                )
                self.micro_expressions.append(me)
    
    def analyze(self) -> ExpressionAnalysis:
        """Analyze collected expression data"""
        if not self.expression_history:
            return ExpressionAnalysis(
                micro_expressions=[],
                expression_distribution={e: 0.0 for e in EXPRESSION_TYPES},
                dominant_expression="unknown",
                emotional_congruence=0.0,
                authentic_smile_count=0,
                stress_indicators=0,
                assessment="insufficient_data",
                recommendations=["No expression data available"]
            )
        
        # Calculate expression distribution
        distribution = {e: 0.0 for e in EXPRESSION_TYPES}
        for state in self.expression_history:
            for expr, score in state.expression_scores.items():
                distribution[expr] += score
        
        total = sum(distribution.values())
        if total > 0:
            distribution = {k: v / total for k, v in distribution.items()}
        
        # Find overall dominant expression
        dominant = max(distribution.keys(), key=lambda k: distribution[k])
        
        # Count authentic smiles (Duchenne - AU6 + AU12)
        authentic_smiles = sum(
            1 for state in self.expression_history
            if state.action_units.get("AU6", 0) > 0.3 and 
               state.action_units.get("AU12", 0) > 0.3
        )
        
        # Count stress indicators
        stress_indicators = len([
            me for me in self.micro_expressions
            if me.expression in ["fearful", "angry", "disgusted"]
        ])
        
        # Calculate emotional congruence (consistency)
        valences = [state.emotional_valence for state in self.expression_history]
        congruence = 1.0 - np.std(valences) if valences else 0.5
        
        # Generate assessment and recommendations
        assessment, recommendations = self._generate_assessment(
            distribution, dominant, 
            authentic_smiles, stress_indicators,
            congruence
        )
        
        return ExpressionAnalysis(
            micro_expressions=self.micro_expressions,
            expression_distribution=distribution,
            dominant_expression=dominant,
            emotional_congruence=float(congruence),
            authentic_smile_count=authentic_smiles,
            stress_indicators=stress_indicators,
            assessment=assessment,
            recommendations=recommendations
        )
    
    def _generate_assessment(
        self,
        distribution: Dict[str, float],
        dominant: str,
        smiles: int,
        stress: int,
        congruence: float
    ) -> Tuple[str, List[str]]:
        """Generate assessment and recommendations"""
        recommendations = []
        
        # Determine overall assessment
        positive_ratio = distribution.get("happy", 0) + distribution.get("neutral", 0) * 0.5
        if positive_ratio > 0.6 and smiles > 3:
            assessment = "positive"
        elif positive_ratio > 0.4:
            assessment = "neutral"
        elif stress > 5:
            assessment = "stressed"
        else:
            assessment = "needs_attention"
        
        # Generate recommendations
        if dominant == "neutral" and smiles < 2:
            recommendations.append(
                "Try to show more positive engagement through natural smiling. "
                "Authentic smiles (reaching your eyes) build rapport with interviewers."
            )
        
        if stress > 3:
            recommendations.append(
                "Some signs of stress were detected. Practice relaxation techniques "
                "before interviews, such as deep breathing."
            )
        
        if congruence < 0.5:
            recommendations.append(
                "Your facial expressions varied significantly. Try to maintain "
                "consistent, positive engagement throughout your responses."
            )
        
        if distribution.get("happy", 0) > 0.5:
            recommendations.append(
                "Good positive expression! Your enthusiasm comes through clearly."
            )
        
        if not recommendations:
            recommendations.append(
                "Your facial expressions were appropriate. Continue practicing "
                "to maintain this level of positive engagement."
            )
        
        return assessment, recommendations
    
    def reset(self):
        """Reset history"""
        self.expression_history = []
        self.micro_expressions = []
        self.prev_landmarks = None
        self.prev_timestamp = None
        self.start_time = None
    
    def close(self):
        """Release resources"""
        self.face_mesh.close()


def detect_micro_expression(landmarks: Dict, prev_landmarks: Dict) -> Dict:
    """Legacy compatibility function"""
    if not landmarks.get("detected", False) or not prev_landmarks:
        return {
            "detected": False,
            "expression": "neutral",
            "intensity": 0.0,
            "confidence": 0.0,
            "duration_ms": 0
        }
    
    return {
        "detected": False,  # Would need full detector for proper detection
        "expression": "neutral",
        "intensity": 0.0,
        "confidence": 0.0,
        "duration_ms": 0
    }


def analyze_expressions(expression_history: List[Dict]) -> Dict:
    """Legacy compatibility function"""
    if not expression_history:
        return {
            "dominant_expression": "neutral",
            "expression_distribution": {exp: 0.0 for exp in EXPRESSION_TYPES},
            "micro_expressions_detected": 0,
            "emotional_congruence": 0.0,
            "assessment": "insufficient_data"
        }
    
    return {
        "dominant_expression": "neutral",
        "expression_distribution": {exp: 1.0 / len(EXPRESSION_TYPES) for exp in EXPRESSION_TYPES},
        "micro_expressions_detected": 0,
        "emotional_congruence": 0.5,
        "assessment": "neutral"
    }
