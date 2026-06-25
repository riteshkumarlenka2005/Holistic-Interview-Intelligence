"""
Eye Tracking Engine.
Uses MediaPipe Face Mesh with refined landmarks to estimate gaze direction.
Tracks eye contact percentage and continuous look-away distraction events.
"""
from typing import Dict, Any, List
import math

class EyeEngine:
    def __init__(self):
        self._mp_face_mesh = None
        self._face_mesh = None

    def _get_model(self):
        if self._mp_face_mesh is None:
            import mediapipe as mp
            self._mp_face_mesh = mp.solutions.face_mesh
            self._face_mesh = self._mp_face_mesh.FaceMesh(
                max_num_faces=1,
                refine_landmarks=True,  # Crucial for Iris tracking
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
        return self._face_mesh

    def _calculate_gaze_ratio(self, landmarks, frame_w, frame_h) -> float:
        """
        Estimates gaze direction by comparing the iris center relative to the eye corners.
        Returns a ratio. ~0.5 means looking straight. <0.4 or >0.6 means looking away.
        """
        # Left eye landmarks (MediaPipe)
        left_eye_left = 33
        left_eye_right = 133
        left_iris_center = 468  # 468 is the center of the left iris when refine_landmarks=True

        p_left = landmarks.landmark[left_eye_left]
        p_right = landmarks.landmark[left_eye_right]
        p_iris = landmarks.landmark[left_iris_center]

        # Convert to pixel coordinates
        x_left, _ = int(p_left.x * frame_w), int(p_left.y * frame_h)
        x_right, _ = int(p_right.x * frame_w), int(p_right.y * frame_h)
        x_iris, _ = int(p_iris.x * frame_w), int(p_iris.y * frame_h)

        eye_width = x_right - x_left
        if eye_width == 0:
            return 0.5

        iris_offset = x_iris - x_left
        return iris_offset / eye_width

    def analyze_frame(self, image_np: "np.ndarray") -> Dict[str, Any]:
        """
        Returns boolean is_looking_at_camera based on gaze ratio.
        """
        import cv2
        model = self._get_model()
        ih, iw, _ = image_np.shape
        
        image_np.flags.writeable = False
        image_rgb = cv2.cvtColor(image_np, cv2.COLOR_BGR2RGB)
        results = model.process(image_rgb)
        image_np.flags.writeable = True

        if not results.multi_face_landmarks:
            return {"is_looking_at_camera": False}

        landmarks = results.multi_face_landmarks[0]
        
        # We need 468 landmarks for Iris tracking. Fallback if not available.
        if len(landmarks.landmark) < 469:
            return {"is_looking_at_camera": False}

        gaze_ratio = self._calculate_gaze_ratio(landmarks, iw, ih)
        
        # Tolerance: 0.40 to 0.60 is generally looking towards the camera center
        is_looking = 0.40 <= gaze_ratio <= 0.60

        return {
            "is_looking_at_camera": is_looking,
            "gaze_ratio": gaze_ratio
        }

    def aggregate_session_metrics(self, frames_data: List[Dict[str, Any]], fps: int = 5) -> Dict[str, Any]:
        """
        Aggregates frame data to calculate eye contact % and distraction events.
        A distraction event is looking away continuously for > 8 seconds.
        """
        if not frames_data:
            return {"eye_contact_percent": 0.0, "distraction_events": 0}

        total_frames = len(frames_data)
        looking_frames = 0
        
        current_away_streak = 0
        distraction_events = 0
        distraction_frame_threshold = 8 * fps  # 8 seconds

        for frame in frames_data:
            if frame.get("is_looking_at_camera"):
                looking_frames += 1
                current_away_streak = 0
            else:
                current_away_streak += 1
                if current_away_streak == distraction_frame_threshold:
                    distraction_events += 1
                    # reset to avoid double counting the same long streak multiple times 
                    # or keep it running depending on definition. Let's reset so 16s = 2 events.
                    current_away_streak = 0

        eye_contact_percent = (looking_frames / total_frames) * 100

        return {
            "eye_contact_percent": round(eye_contact_percent, 1),
            "distraction_events": distraction_events
        }
