"""
Face Analysis Engine.
Uses MediaPipe Face Mesh to analyze facial engagement and head stability.
"""
import math
from typing import Dict, Any, List, Optional

try:
    import cv2
    import numpy as np
    import mediapipe as mp
except ImportError:
    pass  # Allow tests to mock this if not installed


class FaceEngine:
    def __init__(self):
        self._mp_face_mesh = None
        self._face_mesh = None

    def _get_model(self):
        if self._mp_face_mesh is None:
            import mediapipe as mp
            self._mp_face_mesh = mp.solutions.face_mesh
            # max_num_faces=2 so we can detect "multiple_faces" constraint violation
            self._face_mesh = self._mp_face_mesh.FaceMesh(
                max_num_faces=2,
                refine_landmarks=True,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        return self._face_mesh

    def analyze_frame(self, image_np: "np.ndarray") -> Dict[str, Any]:
        """
        Analyzes a single video frame.
        Expects a BGR numpy array from cv2.
        
        Returns:
            Dict containing:
            - face_count (int)
            - pitch, yaw, roll (float)
            - engagement_score (float 0-100)
        """
        model = self._get_model()
        import cv2
        import numpy as np
        
        # To improve performance, optionally mark the image as not writeable
        image_np.flags.writeable = False
        image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        results = model.process(image_rgb)
        image_np.flags.writeable = True

        if not results.multi_face_landmarks:
            return {
                "face_count": 0,
                "pitch": 0.0,
                "yaw": 0.0,
                "roll": 0.0,
                "engagement_score": 0.0
            }
            
        face_count = len(results.multi_face_landmarks)
        
        # We only analyze the first (primary) face for pose
        face_landmarks = results.multi_face_landmarks[0]
        
        # Simple Head Pose Estimation using 2D/3D projection
        ih, iw, _ = image_np.shape
        face_3d = []
        face_2d = []

        # Canonical standard face model points
        # 1: Nose tip, 152: Chin, 33: Left eye left corner, 263: Right eye right corner,
        # 61: Left mouth corner, 291: Right mouth corner
        key_landmarks = [1, 152, 33, 263, 61, 291]

        for idx in key_landmarks:
            lm = face_landmarks.landmark[idx]
            x, y = int(lm.x * iw), int(lm.y * ih)
            face_2d.append([x, y])
            face_3d.append([x, y, lm.z])

        face_2d = np.array(face_2d, dtype=np.float64)
        face_3d = np.array(face_3d, dtype=np.float64)

        focal_length = 1 * iw
        cam_matrix = np.array([
            [focal_length, 0, iw / 2],
            [0, focal_length, ih / 2],
            [0, 0, 1]
        ])
        dist_matrix = np.zeros((4, 1), dtype=np.float64)

        # Solve PnP
        success, rot_vec, trans_vec = cv2.solvePnP(face_3d, face_2d, cam_matrix, dist_matrix)
        
        yaw = 0.0
        pitch = 0.0
        roll = 0.0
        
        if success:
            rmat, _ = cv2.Rodrigues(rot_vec)
            angles, _, _, _, _, _ = cv2.RQDecomp3x3(rmat)
            # OpenCV returns degrees. Typically:
            # angles[0] = pitch (up/down)
            # angles[1] = yaw (left/right)
            # angles[2] = roll (tilt)
            pitch = angles[0] * 360
            yaw = angles[1] * 360
            roll = angles[2] * 360
            
        # Calculate Facial Engagement (0-100)
        # Good engagement = face looking roughly forward
        # Yaw penalty if looking > 20 degrees away
        # Pitch penalty if looking > 20 degrees down or up
        yaw_penalty = max(0, abs(yaw) - 15) * 2
        pitch_penalty = max(0, abs(pitch) - 15) * 2
        
        engagement_score = 100 - yaw_penalty - pitch_penalty
        engagement_score = max(0, min(100, engagement_score))

        return {
            "face_count": face_count,
            "pitch": pitch,
            "yaw": yaw,
            "roll": roll,
            "engagement_score": round(engagement_score, 1)
        }

    def aggregate_session_metrics(self, frames_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregates frame-by-frame data over an answer into a final score.
        Calculates head stability (jitter) by looking at standard deviation of head pose.
        """
        if not frames_data:
            return {"head_stability_score": 0, "avg_engagement": 0, "face_present_percent": 0}
            
        total_frames = len(frames_data)
        frames_with_face = sum(1 for f in frames_data if f.get("face_count", 0) > 0)
        face_present_percent = (frames_with_face / total_frames) * 100

        valid_frames = [f for f in frames_data if f.get("face_count", 0) > 0]
        if not valid_frames:
            return {"head_stability_score": 0, "avg_engagement": 0, "face_present_percent": 0}

        avg_engagement = sum(f.get("engagement_score", 0) for f in valid_frames) / len(valid_frames)
        
        # Head Stability: High variance in yaw/pitch = low stability (jitter)
        import numpy as np
        yaws = [f.get("yaw", 0) for f in valid_frames]
        pitches = [f.get("pitch", 0) for f in valid_frames]
        
        yaw_std = float(np.std(yaws)) if len(yaws) > 1 else 0.0
        pitch_std = float(np.std(pitches)) if len(pitches) > 1 else 0.0
        
        # Baseline good stability: std < 5 degrees. 
        # If std goes to 20+, stability score drops to 0.
        stability_penalty = (yaw_std + pitch_std) * 2
        stability_score = max(0, min(100, 100 - stability_penalty))
        
        return {
            "head_stability_score": round(stability_score, 1),
            "avg_engagement": round(avg_engagement, 1),
            "face_present_percent": round(face_present_percent, 1)
        }
