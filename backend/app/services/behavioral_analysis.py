"""
Behavioral Analysis Service
Real-time emotion detection, confidence/nervousness scoring, and gaze tracking
"""
import base64
import numpy as np
import sys
import os
from collections import deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import asyncio

# Add AI services to path for gaze tracking
ai_services_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'ai-services', 'vision-analysis')
if ai_services_path not in sys.path:
    sys.path.insert(0, os.path.abspath(ai_services_path))

# Add eyeDetect folder for dlib-based fallback gaze tracking
eyedetect_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'eyeDetect')
if eyedetect_path not in sys.path:
    sys.path.insert(0, os.path.abspath(eyedetect_path))

# Lazy imports for heavy dependencies
cv2 = None
FER = None
GazeTracker = None
dlib_process_eye_movement = None


def _load_dependencies():
    """Lazy load OpenCV, FER, and GazeTracker to avoid startup delay"""
    global cv2, FER, GazeTracker
    if cv2 is None:
        import cv2 as _cv2
        cv2 = _cv2
    if FER is None:
        from fer.fer import FER as _FER
        FER = _FER
    if GazeTracker is None:
        try:
            from gaze_tracking import GazeTracker as _GazeTracker
            GazeTracker = _GazeTracker
        except ImportError as e:
            print(f"Warning: GazeTracker not available: {e}")
            GazeTracker = None
    # Load dlib-based eye movement as fallback
    global dlib_process_eye_movement
    if dlib_process_eye_movement is None:
        try:
            from eye_movement import process_eye_movement as _process_eye
            dlib_process_eye_movement = _process_eye
            print("Dlib eye movement module loaded successfully")
        except ImportError as e:
            print(f"Warning: Dlib eye movement not available: {e}")
            dlib_process_eye_movement = None


@dataclass
class BehavioralMetrics:
    """Real-time behavioral analysis metrics including gaze tracking"""
    confidence_score: float  # 0.0 to 1.0
    nervousness_score: float  # 0.0 to 1.0
    behavioral_tag: str  # "CONFIDENT", "NEUTRAL", "NERVOUS"
    emotions: Dict[str, float]  # Raw emotion scores
    face_detected: bool
    face_box: Optional[Tuple[int, int, int, int]] = None  # x, y, w, h
    # Gaze tracking fields
    gaze_direction: str = "center"  # "left", "right", "up", "down", "center"
    gaze_x: float = 0.0  # Normalized gaze X (-1 to 1)
    gaze_y: float = 0.0  # Normalized gaze Y (-1 to 1)
    looking_at_camera: bool = True
    eye_contact_percentage: float = 0.0
    left_iris_position: Optional[Tuple[float, float]] = None  # (x, y) normalized
    right_iris_position: Optional[Tuple[float, float]] = None  # (x, y) normalized
    # Eye box coordinates for rendering eye detection rectangles
    left_eye_box: Optional[Tuple[float, float, float, float]] = None  # (x, y, w, h) normalized
    right_eye_box: Optional[Tuple[float, float, float, float]] = None  # (x, y, w, h) normalized
    # Multi-person detection
    total_faces_detected: int = 1
    multi_person_warning: bool = False
    environment_quality: str = "good"  # "good", "crowded", "noisy"


@dataclass
class AnalysisFrame:
    """Single frame analysis result"""
    timestamp: float
    metrics: BehavioralMetrics


class BehavioralAnalyzer:
    """
    Real-time behavioral analysis using FER (Facial Expression Recognition)
    and MediaPipe gaze tracking for comprehensive behavioral metrics.
    """
    
    def __init__(self, use_mtcnn: bool = True, history_size: int = 20):
        """
        Initialize the behavioral analyzer with emotion and gaze tracking.
        
        Args:
            use_mtcnn: Use MTCNN for more accurate face detection (slower but better)
            history_size: Number of frames to keep for temporal smoothing
        """
        _load_dependencies()
        self.detector = FER(mtcnn=use_mtcnn)
        self.emotion_history: deque = deque(maxlen=history_size)
        self.gaze_history: deque = deque(maxlen=history_size)  # For eye contact tracking
        self.eye_contact_frames: int = 0
        self.total_frames: int = 0
        
        # Initialize gaze tracker if available
        self.gaze_tracker = None
        if GazeTracker is not None:
            try:
                self.gaze_tracker = GazeTracker(
                    min_detection_confidence=0.5,
                    min_tracking_confidence=0.5
                )
                print("GazeTracker initialized successfully")
            except Exception as e:
                print(f"Failed to initialize GazeTracker: {e}")
        
        self._is_initialized = True
    
    def _get_gaze_direction_label(self, gaze_x: float, gaze_y: float, threshold: float = 0.15) -> str:
        """Convert gaze coordinates to direction label"""
        if abs(gaze_x) < threshold and abs(gaze_y) < threshold:
            return "center"
        elif abs(gaze_x) > abs(gaze_y):
            return "left" if gaze_x < 0 else "right"
        else:
            return "up" if gaze_y < 0 else "down"
        
    def calculate_confidence_nervousness(self, emotions: Dict[str, float]) -> Tuple[float, float]:
        """
        Calculate confidence and nervousness scores from raw emotions.
        
        General Scoring Logic:
        - Confidence is based on 'Emotional Presence'
        - If you are Neutral or Happy and NOT showing high Fear, you are Confident
        - Nervousness focuses on Fear and Surprise as "jitter" emotions
        
        Args:
            emotions: Dictionary of emotion scores from FER
            
        Returns:
            Tuple of (confidence_score, nervousness_score) both 0.0 to 1.0
        """
        # Extract emotion values with defaults
        f = emotions.get('fear', 0)
        s = emotions.get('sad', 0)
        su = emotions.get('surprise', 0)
        n = emotions.get('neutral', 0)
        h = emotions.get('happy', 0)
        a = emotions.get('angry', 0)

        # --- REFINED CONFIDENCE MATH ---
        # Reward Neutral and Happy almost equally as "Positive Presence"
        positive_presence = (n * 0.8) + (h * 1.0)
        # Negative emotions only reduce confidence if they are significant (>15%)
        penalty = (f * 0.6) + (s * 0.3) + (a * 0.1)
        
        # Boost factor: If mostly neutral/happy, bump the score up
        conf_base = positive_presence - penalty
        conf_final = (conf_base + 0.2) if positive_presence > 0.4 else conf_base

        # --- REFINED NERVOUSNESS MATH ---
        # Focuses on the "Jitter" emotions: Fear and Surprise
        nerv_final = (f * 0.7) + (su * 0.3)

        return float(np.clip(conf_final, 0, 1)), float(np.clip(nerv_final, 0, 1))

    def get_behavioral_tag(self, confidence: float, nervousness: float) -> str:
        """Determine behavioral tag based on scores"""
        if nervousness > 0.4:
            return "NERVOUS"
        elif confidence > 0.6:
            return "CONFIDENT"
        return "NEUTRAL"

    def calculate_eye_boxes(self, face_box: Tuple[int, int, int, int], frame_w: int, frame_h: int) -> Tuple[Optional[Tuple[float, float, float, float]], Optional[Tuple[float, float, float, float]]]:
        """
        Calculate normalized eye bounding boxes from face box.
        Uses anatomical proportions: eyes are typically in upper third of face.
        
        Args:
            face_box: (x, y, width, height) of face in pixels
            frame_w: Frame width for normalization
            frame_h: Frame height for normalization
            
        Returns:
            Tuple of (left_eye_box, right_eye_box) normalized to 0-1 range
        """
        if not face_box or frame_w <= 0 or frame_h <= 0:
            return None, None
        
        fx, fy, fw, fh = face_box
        
        # Eye region calculations based on facial proportions
        # Eyes are typically at ~25-35% from top of face, ~15% of face height
        eye_y = fy + int(fh * 0.25)  # Eyes start at 25% from top of face
        eye_h = int(fh * 0.12)       # Eye height is ~12% of face height
        eye_w = int(fw * 0.25)       # Each eye width is ~25% of face width
        
        # Left eye (from subject's perspective, right side of image due to mirror)
        left_eye_x = fx + int(fw * 0.58)  # Left eye at 58% from left of face
        left_eye_box = (
            left_eye_x / frame_w,
            eye_y / frame_h,
            eye_w / frame_w,
            eye_h / frame_h
        )
        
        # Right eye (from subject's perspective, left side of image due to mirror)
        right_eye_x = fx + int(fw * 0.17)  # Right eye at 17% from left of face
        right_eye_box = (
            right_eye_x / frame_w,
            eye_y / frame_h,
            eye_w / frame_w,
            eye_h / frame_h
        )
        
        return left_eye_box, right_eye_box

    def analyze_frame(self, frame: np.ndarray, timestamp: float = 0.0) -> BehavioralMetrics:
        """
        Analyze a single video frame for behavioral metrics including gaze.
        Uses intelligent face selection to track the primary user (largest, center-most face).
        
        Args:
            frame: BGR image frame (numpy array)
            timestamp: Optional timestamp for the frame
            
        Returns:
            BehavioralMetrics with confidence, nervousness, emotions, gaze, and face info
        """
        # Default metrics for no face detected
        default_emotions = {
            'happy': 0.0, 'neutral': 0.0, 'fear': 0.0,
            'sad': 0.0, 'angry': 0.0, 'surprise': 0.0, 'disgust': 0.0
        }
        
        # Default gaze values
        gaze_direction = "center"
        gaze_x = 0.0
        gaze_y = 0.0
        looking_at_camera = True
        left_iris = None
        right_iris = None
        h, w = frame.shape[:2] if frame is not None else (720, 1280)
        frame_center_x = w / 2
        
        # Track frame count for eye contact
        self.total_frames += 1
        
        try:
            # === Gaze tracking for direction (uses MediaPipe, fallback to dlib) ===
            mediapipe_success = False
            if self.gaze_tracker is not None:
                try:
                    gaze_point = self.gaze_tracker.process_frame(frame, timestamp)
                    if gaze_point and gaze_point.confidence > 0.3:
                        mediapipe_success = True
                        gaze_x, gaze_y = gaze_point.gaze_direction
                        looking_at_camera = gaze_point.looking_at_camera
                        gaze_direction = self._get_gaze_direction_label(gaze_x, gaze_y)
                        
                        # If MediaPipe has iris positions, use those for higher accuracy
                        if gaze_point.left_iris_position and gaze_point.right_iris_position:
                            lx, ly = gaze_point.left_iris_position
                            rx, ry = gaze_point.right_iris_position
                            left_iris = (lx / w, ly / h) if w > 0 and h > 0 else left_iris
                            right_iris = (rx / w, ry / h) if w > 0 and h > 0 else right_iris
                except Exception as gaze_err:
                    print(f"MediaPipe gaze tracking error: {gaze_err}")
            
            # Fallback to dlib-based gaze direction estimation
            if not mediapipe_success and dlib_process_eye_movement is not None:
                try:
                    _, dlib_gaze_direction = dlib_process_eye_movement(frame.copy())
                    # Parse dlib gaze direction (e.g., "Looking Center", "Looking Left")
                    if dlib_gaze_direction:
                        direction_lower = dlib_gaze_direction.lower()
                        if "center" in direction_lower or "screen" in direction_lower:
                            gaze_direction = "center"
                            looking_at_camera = True
                        elif "left" in direction_lower:
                            gaze_direction = "left"
                            looking_at_camera = False
                            gaze_x = -0.5
                        elif "right" in direction_lower:
                            gaze_direction = "right"
                            looking_at_camera = False
                            gaze_x = 0.5
                        elif "up" in direction_lower:
                            gaze_direction = "up"
                            looking_at_camera = False
                            gaze_y = -0.5
                        elif "down" in direction_lower:
                            gaze_direction = "down"
                            looking_at_camera = False
                            gaze_y = 0.5
                except Exception as dlib_err:
                    print(f"Dlib gaze tracking error: {dlib_err}")
            
            # If neither gaze tracker worked but we have a face, use face position to estimate
            # If face is centered, assume user is looking at camera
            if not mediapipe_success and dlib_process_eye_movement is None:
                # Default to looking at camera when no gaze tracker is available
                # This will be refined when face detection runs below
                looking_at_camera = True
                gaze_direction = "center"

            
            # Update eye contact frames based on looking_at_camera
            if looking_at_camera and gaze_direction == "center":
                self.eye_contact_frames += 1
            
            # Calculate eye contact percentage using recent frames window for responsiveness
            # Use a sliding window of last 50 frames for more dynamic updates
            recent_window = min(self.total_frames, 50)
            if recent_window > 0:
                # Calculate based on gaze direction for recent responsiveness
                # If currently looking at center, boost the percentage
                if gaze_direction == "center":
                    eye_contact_pct = min(100.0, (self.eye_contact_frames / self.total_frames * 100) + 20)
                else:
                    eye_contact_pct = max(0.0, (self.eye_contact_frames / self.total_frames * 100) - 20)
            else:
                eye_contact_pct = 0.0
            
            # Emotion detection - get ALL faces
            results = self.detector.detect_emotions(frame)
            
            total_faces = len(results) if results else 0
            multi_person_warning = total_faces > 1
            environment_quality = "good"
            
            if total_faces > 2:
                environment_quality = "crowded"
            elif total_faces > 1:
                environment_quality = "busy"
            
            if not results:
                return BehavioralMetrics(
                    confidence_score=0.0,
                    nervousness_score=0.0,
                    behavioral_tag="NO_FACE",
                    emotions=default_emotions,
                    face_detected=False,
                    gaze_direction=gaze_direction,
                    gaze_x=gaze_x,
                    gaze_y=gaze_y,
                    looking_at_camera=looking_at_camera,
                    eye_contact_percentage=eye_contact_pct,
                    left_iris_position=left_iris,
                    right_iris_position=right_iris,
                    total_faces_detected=0,
                    multi_person_warning=False,
                    environment_quality="good"
                )
            
            # === PRIMARY FACE SELECTION ALGORITHM ===
            # Select the face that is: 1) Largest (closest to camera), 2) Most centered
            primary_face = None
            best_score = -1
            
            for face in results:
                box = face['box']
                face_x, face_y, face_w, face_h = box
                face_area = face_w * face_h
                face_center_x = face_x + (face_w / 2)
                
                # Calculate center distance (0 = perfectly centered)
                center_distance = abs(face_center_x - frame_center_x) / frame_center_x
                center_score = 1.0 - min(center_distance, 1.0)  # 0-1 (1 = centered)
                
                # Combine area and center scores
                # Weight: 60% size, 40% center position
                normalized_area = face_area / (w * h)  # 0-1 based on frame size
                combined_score = (normalized_area * 100 * 0.6) + (center_score * 0.4)
                
                if combined_score > best_score:
                    best_score = combined_score
                    primary_face = face
            
            # Use the primary face
            face = primary_face
            box = face['box']
            current_emotions = face['emotions']
            
            # === Extract eye detection data using face box ===
            from .dlib_eye_detector import extract_eye_data
            
            face_box_tuple = (int(box[0]), int(box[1]), int(box[2]), int(box[3]))
            eye_data = extract_eye_data(frame, w, h, face_box_tuple)
            
            # Override iris positions if we got pupils from eye detection
            if eye_data["left_pupil"]:
                left_iris = eye_data["left_pupil"]
            if eye_data["right_pupil"]:
                right_iris = eye_data["right_pupil"]
            
            left_eye_box_from_detector = eye_data["left_eye_box"]
            right_eye_box_from_detector = eye_data["right_eye_box"]
            
            # Calculate raw scores
            conf_raw, nerv_raw = self.calculate_confidence_nervousness(current_emotions)
            
            # Temporal smoothing to reduce jitter
            self.emotion_history.append((conf_raw, nerv_raw))
            conf_smooth = float(np.mean([x[0] for x in self.emotion_history]))
            nerv_smooth = float(np.mean([x[1] for x in self.emotion_history]))
            
            # Determine behavioral tag
            tag = self.get_behavioral_tag(conf_smooth, nerv_smooth)
            
            # Use eye boxes from detector
            if left_eye_box_from_detector and right_eye_box_from_detector:
                left_eye_box = left_eye_box_from_detector
                right_eye_box = right_eye_box_from_detector
            else:
                # Fallback to calculated eye boxes
                left_eye_box, right_eye_box = self.calculate_eye_boxes(face_box_tuple, w, h)
            
            # Normalize face_box coordinates for consistent rendering
            # Frontend will multiply by its video dimensions
            normalized_face_box = (
                face_box_tuple[0] / w,  # x normalized
                face_box_tuple[1] / h,  # y normalized
                face_box_tuple[2] / w,  # width normalized
                face_box_tuple[3] / h   # height normalized
            )
            
            return BehavioralMetrics(
                confidence_score=conf_smooth,
                nervousness_score=nerv_smooth,
                behavioral_tag=tag,
                emotions=current_emotions,
                face_detected=True,
                face_box=normalized_face_box,  # Send normalized coordinates
                gaze_direction=gaze_direction,
                gaze_x=gaze_x,
                gaze_y=gaze_y,
                looking_at_camera=looking_at_camera,
                eye_contact_percentage=eye_contact_pct,
                left_iris_position=left_iris,
                right_iris_position=right_iris,
                left_eye_box=left_eye_box,
                right_eye_box=right_eye_box,
                total_faces_detected=total_faces,
                multi_person_warning=multi_person_warning,
                environment_quality=environment_quality
            )
            
        except Exception as e:
            print(f"Error analyzing frame: {e}")
            return BehavioralMetrics(
                confidence_score=0.0,
                nervousness_score=0.0,
                behavioral_tag="ERROR",
                emotions=default_emotions,
                face_detected=False
            )

    def decode_base64_frame(self, base64_data: str) -> Optional[np.ndarray]:
        """
        Decode a base64 encoded image to numpy array.
        
        Args:
            base64_data: Base64 encoded image string (may include data URI prefix)
            
        Returns:
            BGR image as numpy array, or None if decoding fails
        """
        try:
            # Remove data URI prefix if present
            if ',' in base64_data:
                base64_data = base64_data.split(',')[1]
            
            # Decode base64 to bytes
            img_bytes = base64.b64decode(base64_data)
            
            # Convert to numpy array
            nparr = np.frombuffer(img_bytes, np.uint8)
            
            # Decode image
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            return frame
            
        except Exception as e:
            print(f"Error decoding frame: {e}")
            return None

    def analyze_base64_frame(self, base64_data: str, timestamp: float = 0.0) -> BehavioralMetrics:
        """
        Analyze a base64 encoded frame.
        
        Args:
            base64_data: Base64 encoded image
            timestamp: Optional timestamp
            
        Returns:
            BehavioralMetrics
        """
        frame = self.decode_base64_frame(base64_data)
        
        if frame is None:
            return BehavioralMetrics(
                confidence_score=0.0,
                nervousness_score=0.0,
                behavioral_tag="DECODE_ERROR",
                emotions={},
                face_detected=False
            )
        
        return self.analyze_frame(frame, timestamp)

    def reset(self):
        """Reset the emotion and gaze history for a new session"""
        self.emotion_history.clear()
        self.gaze_history.clear()
        self.eye_contact_frames = 0
        self.total_frames = 0
        if self.gaze_tracker is not None:
            self.gaze_tracker.reset()

    def get_session_summary(self) -> Dict:
        """Get summary statistics for the current session"""
        if not self.emotion_history:
            return {
                "avg_confidence": 0.0,
                "avg_nervousness": 0.0,
                "frames_analyzed": 0
            }
        
        confidences = [x[0] for x in self.emotion_history]
        nervousness = [x[1] for x in self.emotion_history]
        
        return {
            "avg_confidence": float(np.mean(confidences)),
            "avg_nervousness": float(np.mean(nervousness)),
            "max_confidence": float(np.max(confidences)),
            "min_confidence": float(np.min(confidences)),
            "max_nervousness": float(np.max(nervousness)),
            "min_nervousness": float(np.min(nervousness)),
            "frames_analyzed": len(self.emotion_history)
        }


# Singleton instance for reuse
_analyzer_instance: Optional[BehavioralAnalyzer] = None


def get_analyzer(use_mtcnn: bool = True) -> BehavioralAnalyzer:
    """Get or create a singleton BehavioralAnalyzer instance"""
    global _analyzer_instance
    if _analyzer_instance is None:
        _analyzer_instance = BehavioralAnalyzer(use_mtcnn=use_mtcnn)
    return _analyzer_instance


def analyze_frame_sync(frame: np.ndarray) -> Dict:
    """
    Synchronous frame analysis for REST API.
    
    Args:
        frame: BGR image as numpy array
        
    Returns:
        Dictionary with analysis results
    """
    analyzer = get_analyzer()
    metrics = analyzer.analyze_frame(frame)
    
    return {
        "confidence_score": metrics.confidence_score,
        "nervousness_score": metrics.nervousness_score,
        "behavioral_tag": metrics.behavioral_tag,
        "emotions": metrics.emotions,
        "face_detected": metrics.face_detected,
        "face_box": metrics.face_box,
        "gaze_direction": metrics.gaze_direction,
        "gaze_x": metrics.gaze_x,
        "gaze_y": metrics.gaze_y,
        "looking_at_camera": metrics.looking_at_camera,
        "eye_contact_percentage": metrics.eye_contact_percentage,
        "left_iris_position": metrics.left_iris_position,
        "right_iris_position": metrics.right_iris_position,
        "total_faces_detected": metrics.total_faces_detected,
        "multi_person_warning": metrics.multi_person_warning,
        "environment_quality": metrics.environment_quality
    }


async def analyze_frame_async(base64_data: str, timestamp: float = 0.0) -> Dict:
    """
    Async frame analysis for WebSocket streaming.
    
    Args:
        base64_data: Base64 encoded image
        timestamp: Frame timestamp
        
    Returns:
        Dictionary with analysis results
    """
    # Run CPU-intensive analysis in thread pool
    loop = asyncio.get_event_loop()
    analyzer = get_analyzer()
    
    metrics = await loop.run_in_executor(
        None,
        analyzer.analyze_base64_frame,
        base64_data,
        timestamp
    )
    
    return {
        "timestamp": timestamp,
        "confidence_score": metrics.confidence_score,
        "nervousness_score": metrics.nervousness_score,
        "behavioral_tag": metrics.behavioral_tag,
        "emotions": metrics.emotions,
        "face_detected": metrics.face_detected,
        "face_box": metrics.face_box,
        "gaze_direction": metrics.gaze_direction,
        "gaze_x": metrics.gaze_x,
        "gaze_y": metrics.gaze_y,
        "looking_at_camera": metrics.looking_at_camera,
        "eye_contact_percentage": metrics.eye_contact_percentage,
        "left_iris_position": metrics.left_iris_position,
        "right_iris_position": metrics.right_iris_position,
        "total_faces_detected": metrics.total_faces_detected,
        "multi_person_warning": metrics.multi_person_warning,
        "environment_quality": metrics.environment_quality
    }
