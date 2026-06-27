"""
Vision Pipeline — Single Inference Architecture for MediaPipe FaceMesh.

Runs a single MediaPipe FaceMesh inference per frame and distributes
the landmarks to sub-engines (Face, Eye, Mouth).

Outputs combined metrics dictionary for the frame.
"""
from typing import Dict, Any, List
import numpy as np
import cv2

try:
    import mediapipe as mp
except ImportError:
    pass

from app.services.face_engine import FaceEngine
from app.services.eye_engine import EyeEngine
from app.services.mouth_engine import MouthEngine


class VisionPipeline:
    def __init__(self):
        self._mp_face_mesh = mp.solutions.face_mesh
        # Single shared FaceMesh model for the entire pipeline
        self._face_mesh = self._mp_face_mesh.FaceMesh(
            max_num_faces=2,          # Keep 2 to detect multiple faces for IntegrityEngine
            refine_landmarks=True,    # Crucial for Iris tracking (478 landmarks)
            min_detection_confidence=0.5,
            min_tracking_confidence=0.5
        )
        
        # Sub-engines (Stateless processors)
        self.face_engine = FaceEngine()
        self.eye_engine = EyeEngine()
        self.mouth_engine = MouthEngine()

    def process_frame(self, image_np: np.ndarray) -> Dict[str, Any]:
        """
        Runs single inference on the frame and delegates landmarks.
        """
        ih, iw, _ = image_np.shape
        
        image_np.flags.writeable = False
        image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        results = self._face_mesh.process(image_rgb)
        image_np.flags.writeable = True

        # Default empty metrics if no face detected
        if not results.multi_face_landmarks:
            return {
                "face_count": 0,
                "pitch": 0.0,
                "yaw": 0.0,
                "roll": 0.0,
                "engagement_score": 0.0,
                "is_looking_at_camera": False,
                "gaze_ratio_x": 0.5,
                "gaze_ratio_y": 0.5,
                "is_blinking": False,
                "is_mouth_open": False,
            }

        face_count = len(results.multi_face_landmarks)
        # We only analyze the primary face for detailed tracking
        landmarks = results.multi_face_landmarks[0]

        # Pass landmarks to sub-engines
        face_metrics = self.face_engine.analyze_landmarks(landmarks, iw, ih, face_count)
        eye_metrics = self.eye_engine.analyze_landmarks(landmarks, iw, ih)
        mouth_metrics = self.mouth_engine.analyze_landmarks(landmarks, iw, ih)

        # Combine results
        return {
            **face_metrics,
            **eye_metrics,
            **mouth_metrics
        }

    def aggregate_session_metrics(self, frames_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Delegates rolling window metric aggregation to sub-engines.
        """
        face_agg = self.face_engine.aggregate_session_metrics(frames_data)
        eye_agg = self.eye_engine.aggregate_session_metrics(frames_data, fps=5)
        mouth_agg = self.mouth_engine.aggregate_session_metrics(frames_data)
        
        return {
            **face_agg,
            **eye_agg,
            **mouth_agg
        }
