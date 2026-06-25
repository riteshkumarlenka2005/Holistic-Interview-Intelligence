"""
Face Landmarks Detection Module
Detects facial landmarks using MediaPipe for expression and gaze analysis
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
import numpy as np  # type: ignore[import-untyped]

# Lazy imports - typed as Any to satisfy type checkers
mp: Any = None
cv2: Any = None


def _load_mediapipe():
    """Lazy load MediaPipe"""
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


# Key facial landmark indices for MediaPipe Face Mesh
LANDMARK_INDICES = {
    # Eye landmarks
    "left_eye": [33, 7, 163, 144, 145, 153, 154, 155, 133, 173, 157, 158, 159, 160, 161, 246],
    "right_eye": [362, 382, 381, 380, 374, 373, 390, 249, 263, 466, 388, 387, 386, 385, 384, 398],
    "left_iris": [468, 469, 470, 471, 472],
    "right_iris": [473, 474, 475, 476, 477],
    "left_eye_center": [468],  # Iris center
    "right_eye_center": [473],  # Iris center
    
    # Eyebrows
    "left_eyebrow": [70, 63, 105, 66, 107, 55, 65, 52, 53, 46],
    "right_eyebrow": [300, 293, 334, 296, 336, 285, 295, 282, 283, 276],
    
    # Nose
    "nose_tip": [1],
    "nose_bridge": [6, 197, 195, 5],
    
    # Mouth
    "upper_lip": [61, 185, 40, 39, 37, 0, 267, 269, 270, 409, 291],
    "lower_lip": [146, 91, 181, 84, 17, 314, 405, 321, 375, 291],
    "mouth_outer": [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185],
    
    # Face contour
    "face_oval": [10, 338, 297, 332, 284, 251, 389, 356, 454, 323, 361, 288, 397, 365, 379, 378, 400, 377, 152, 148, 176, 149, 150, 136, 172, 58, 132, 93, 234, 127, 162, 21, 54, 103, 67, 109],
    
    # Forehead points
    "forehead": [10, 67, 109, 10, 338, 297],
}


@dataclass
class FaceLandmarks:
    """Detected face landmarks"""
    landmarks: np.ndarray  # (478, 3) array of landmarks
    confidence: float
    face_detected: bool
    bounding_box: Optional[Tuple[int, int, int, int]]  # x, y, w, h


@dataclass
class EyeMetrics:
    """Eye-specific measurements"""
    left_eye_openness: float  # 0-1, 0=closed, 1=fully open
    right_eye_openness: float
    left_eye_center: Tuple[float, float]
    right_eye_center: Tuple[float, float]
    eye_aspect_ratio: float
    blink_detected: bool


@dataclass
class MouthMetrics:
    """Mouth-specific measurements"""
    mouth_openness: float  # 0-1
    mouth_width: float  # Relative to face width
    smile_score: float  # 0-1, likelihood of smiling
    lip_distance: float


class FaceLandmarkDetector:
    """
    MediaPipe-based face landmark detection.
    Detects 478 facial landmarks for detailed face analysis.
    """
    
    def __init__(
        self,
        static_image_mode: bool = False,
        max_num_faces: int = 1,
        refine_landmarks: bool = True,
        min_detection_confidence: float = 0.5,
        min_tracking_confidence: float = 0.5
    ):
        """
        Initialize face landmark detector.
        
        Args:
            static_image_mode: If True, treats each image independently
            max_num_faces: Maximum number of faces to detect
            refine_landmarks: If True, refines landmarks around eyes and lips
            min_detection_confidence: Minimum detection confidence threshold
            min_tracking_confidence: Minimum tracking confidence threshold
        """
        _load_mediapipe()
        
        self.mp_face_mesh = mp.solutions.face_mesh
        self.face_mesh = self.mp_face_mesh.FaceMesh(
            static_image_mode=static_image_mode,
            max_num_faces=max_num_faces,
            refine_landmarks=refine_landmarks,
            min_detection_confidence=min_detection_confidence,
            min_tracking_confidence=min_tracking_confidence
        )
        self.refine_landmarks = refine_landmarks
    
    def detect(
        self,
        frame: np.ndarray,
        return_image: bool = False
    ) -> Union[FaceLandmarks, Tuple[FaceLandmarks, np.ndarray]]:
        """
        Detect face landmarks in a frame.
        
        Args:
            frame: BGR image frame
            return_image: If True, return annotated image
            
        Returns:
            FaceLandmarks object (and optionally annotated image)
        """
        # Convert to RGB
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        h, w = frame.shape[:2]
        
        # Process frame
        results = self.face_mesh.process(rgb_frame)
        
        if not results.multi_face_landmarks:
            empty_landmarks = FaceLandmarks(
                landmarks=np.zeros((478, 3)),
                confidence=0.0,
                face_detected=False,
                bounding_box=None
            )
            if return_image:
                return empty_landmarks, frame
            return empty_landmarks
        
        # Get first face
        face_landmarks = results.multi_face_landmarks[0]
        
        # Convert to numpy array
        landmarks = np.array([
            [lm.x * w, lm.y * h, lm.z * w]
            for lm in face_landmarks.landmark
        ])
        
        # Calculate bounding box
        x_min = int(np.min(landmarks[:, 0]))
        x_max = int(np.max(landmarks[:, 0]))
        y_min = int(np.min(landmarks[:, 1]))
        y_max = int(np.max(landmarks[:, 1]))
        bbox = (x_min, y_min, x_max - x_min, y_max - y_min)
        
        result = FaceLandmarks(
            landmarks=landmarks,
            confidence=1.0,  # MediaPipe doesn't provide per-face confidence
            face_detected=True,
            bounding_box=bbox
        )
        
        if return_image:
            annotated = self._draw_landmarks(frame.copy(), landmarks)
            return result, annotated
        
        return result
    
    def _draw_landmarks(
        self,
        image: np.ndarray,
        landmarks: np.ndarray
    ) -> np.ndarray:
        """Draw landmarks on image"""
        for point in landmarks:
            x, y = int(point[0]), int(point[1])
            cv2.circle(image, (x, y), 1, (0, 255, 0), -1)
        return image
    
    def get_eye_metrics(self, landmarks: np.ndarray) -> EyeMetrics:
        """
        Calculate eye-specific metrics.
        
        Args:
            landmarks: Face landmarks array
            
        Returns:
            EyeMetrics with eye measurements
        """
        # Get eye landmarks
        left_eye = landmarks[LANDMARK_INDICES["left_eye"]]
        right_eye = landmarks[LANDMARK_INDICES["right_eye"]]
        
        # Calculate Eye Aspect Ratio (EAR)
        left_ear = self._calculate_ear(left_eye)
        right_ear = self._calculate_ear(right_eye)
        avg_ear = (left_ear + right_ear) / 2
        
        # Eye openness (normalized)
        left_openness = min(1.0, left_ear / 0.3)
        right_openness = min(1.0, right_ear / 0.3)
        
        # Eye centers (if iris landmarks available)
        if len(landmarks) > 470 and self.refine_landmarks:
            left_center = tuple(landmarks[468][:2])
            right_center = tuple(landmarks[473][:2])
        else:
            left_center = tuple(np.mean(left_eye[:, :2], axis=0))
            right_center = tuple(np.mean(right_eye[:, :2], axis=0))
        
        # Blink detection
        blink_detected = avg_ear < 0.2
        
        return EyeMetrics(
            left_eye_openness=float(left_openness),
            right_eye_openness=float(right_openness),
            left_eye_center=left_center,
            right_eye_center=right_center,
            eye_aspect_ratio=float(avg_ear),
            blink_detected=blink_detected
        )
    
    def _calculate_ear(self, eye_landmarks: np.ndarray) -> float:
        """Calculate Eye Aspect Ratio (EAR)"""
        # Simplified EAR calculation
        if len(eye_landmarks) < 6:
            return 0.3
        
        # Vertical distances
        v1 = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        v2 = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        
        # Horizontal distance
        h = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        if h == 0:
            return 0.3
        
        ear = (v1 + v2) / (2.0 * h)
        return float(ear)
    
    def get_mouth_metrics(self, landmarks: np.ndarray) -> MouthMetrics:
        """
        Calculate mouth-specific metrics.
        
        Args:
            landmarks: Face landmarks array
            
        Returns:
            MouthMetrics with mouth measurements
        """
        # Get mouth landmarks
        upper_lip = landmarks[LANDMARK_INDICES["upper_lip"]]
        lower_lip = landmarks[LANDMARK_INDICES["lower_lip"]]
        
        # Lip distance (openness)
        upper_center = landmarks[13]  # Upper lip center
        lower_center = landmarks[14]  # Lower lip center
        lip_distance = np.linalg.norm(upper_center - lower_center)
        
        # Face height for normalization
        face_height = np.linalg.norm(landmarks[10] - landmarks[152])
        
        # Normalized openness
        mouth_openness = min(1.0, lip_distance / (face_height * 0.15))
        
        # Mouth width
        left_corner = landmarks[61]
        right_corner = landmarks[291]
        mouth_width_abs = np.linalg.norm(left_corner - right_corner)
        
        # Face width for normalization
        face_width = np.linalg.norm(landmarks[234] - landmarks[454])
        mouth_width = mouth_width_abs / face_width if face_width > 0 else 0
        
        # Smile detection (mouth corners raised)
        mouth_center_y = (upper_center[1] + lower_center[1]) / 2
        corner_avg_y = (left_corner[1] + right_corner[1]) / 2
        smile_score = max(0, min(1, (mouth_center_y - corner_avg_y) / 20 + 0.5))
        
        return MouthMetrics(
            mouth_openness=float(mouth_openness),
            mouth_width=float(mouth_width),
            smile_score=float(smile_score),
            lip_distance=float(lip_distance)
        )
    
    def get_head_pose(
        self,
        landmarks: np.ndarray,
        image_size: Tuple[int, int]
    ) -> Dict[str, float]:
        """
        Estimate head pose (pitch, yaw, roll).
        
        Args:
            landmarks: Face landmarks array
            image_size: (width, height) of image
            
        Returns:
            Dictionary with pitch, yaw, roll angles in degrees
        """
        w, h = image_size
        
        # 3D model points
        model_points = np.array([
            (0.0, 0.0, 0.0),        # Nose tip
            (0.0, -330.0, -65.0),   # Chin
            (-225.0, 170.0, -135.0),  # Left eye corner
            (225.0, 170.0, -135.0),   # Right eye corner
            (-150.0, -150.0, -125.0), # Left mouth corner
            (150.0, -150.0, -125.0)   # Right mouth corner
        ], dtype=np.float64)
        
        # 2D image points
        image_points = np.array([
            landmarks[1][:2],    # Nose tip
            landmarks[199][:2],  # Chin
            landmarks[33][:2],   # Left eye corner
            landmarks[263][:2],  # Right eye corner
            landmarks[61][:2],   # Left mouth corner
            landmarks[291][:2]   # Right mouth corner
        ], dtype=np.float64)
        
        # Camera matrix
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1]
        ], dtype=np.float64)
        
        dist_coeffs = np.zeros((4, 1))
        
        # Solve PnP
        success, rotation_vector, translation_vector = cv2.solvePnP(
            model_points,
            image_points,
            camera_matrix,
            dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE
        )
        
        if not success:
            return {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}
        
        # Convert to rotation matrix
        rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
        
        # Extract Euler angles
        sy = np.sqrt(rotation_matrix[0, 0] ** 2 + rotation_matrix[1, 0] ** 2)
        singular = sy < 1e-6
        
        if not singular:
            x = np.arctan2(rotation_matrix[2, 1], rotation_matrix[2, 2])
            y = np.arctan2(-rotation_matrix[2, 0], sy)
            z = np.arctan2(rotation_matrix[1, 0], rotation_matrix[0, 0])
        else:
            x = np.arctan2(-rotation_matrix[1, 2], rotation_matrix[1, 1])
            y = np.arctan2(-rotation_matrix[2, 0], sy)
            z = 0
        
        # Convert to degrees
        pitch = float(np.degrees(x))
        yaw = float(np.degrees(y))
        roll = float(np.degrees(z))
        
        return {"pitch": pitch, "yaw": yaw, "roll": roll}
    
    def close(self):
        """Release resources"""
        self.face_mesh.close()


def detect_landmarks(frame: np.ndarray) -> Dict:
    """
    Convenience function to detect face landmarks.
    
    Args:
        frame: BGR image frame
        
    Returns:
        Dictionary with landmarks and metrics
    """
    detector = FaceLandmarkDetector()
    result = detector.detect(frame)
    
    if not result.face_detected:
        return {
            "detected": False,
            "landmarks": [],
            "eye_metrics": None,
            "mouth_metrics": None
        }
    
    eye_metrics = detector.get_eye_metrics(result.landmarks)
    mouth_metrics = detector.get_mouth_metrics(result.landmarks)
    
    return {
        "detected": True,
        "landmarks": result.landmarks.tolist(),
        "bounding_box": result.bounding_box,
        "eye_metrics": {
            "left_openness": eye_metrics.left_eye_openness,
            "right_openness": eye_metrics.right_eye_openness,
            "ear": eye_metrics.eye_aspect_ratio,
            "blink": eye_metrics.blink_detected
        },
        "mouth_metrics": {
            "openness": mouth_metrics.mouth_openness,
            "width": mouth_metrics.mouth_width,
            "smile_score": mouth_metrics.smile_score
        }
    }
