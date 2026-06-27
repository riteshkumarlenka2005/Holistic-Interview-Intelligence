import cv2
import numpy as np
from .types import CameraStability
from .models import ConfidentValue
from .utils import RollingAverage

class CameraAnalyzer:
    def __init__(self):
        self.prev_gray = None
        self.prev_pts = None
        self.motion_smoother = RollingAverage(window_size_seconds=1.5)

    def process(self, frame_gray: np.ndarray, fps: float) -> dict:
        result = {
            "fps": ConfidentValue(value=fps, confidence=95.0),
            "resolution": f"{frame_gray.shape[1]}x{frame_gray.shape[0]}",
            "sharpness": ConfidentValue(value=100.0, confidence=90.0),
            "brightness": ConfidentValue(value=100.0, confidence=90.0),
            "exposure": ConfidentValue(value=100.0, confidence=90.0),
            "stability": ConfidentValue(value=CameraStability.STABLE, confidence=95.0),
            "frame_quality_score": 100,
            "blocks": [],
            "warnings": []
        }
        
        # 1. Optical Flow Stability Check (Lucas-Kanade)
        motion_magnitude = 0.0
        if self.prev_gray is not None and self.prev_pts is not None and len(self.prev_pts) > 0:
            next_pts, status, err = cv2.calcOpticalFlowPyrLK(self.prev_gray, frame_gray, self.prev_pts, None)
            if next_pts is not None and status is not None:
                good_new = next_pts[status == 1]
                good_old = self.prev_pts[status == 1]
                if len(good_new) > 0:
                    displacements = np.linalg.norm(good_new - good_old, axis=1)
                    motion_magnitude = float(np.mean(displacements))
        
        # Re-detect features to track every few frames (or if lost)
        if self.prev_pts is None or len(self.prev_pts) < 10:
            # Mask out the center to avoid tracking the person's face moving naturally
            mask = np.ones_like(frame_gray) * 255
            h, w = frame_gray.shape
            cv2.rectangle(mask, (int(w*0.3), int(h*0.2)), (int(w*0.7), int(h*0.8)), 0, -1)
            self.prev_pts = cv2.goodFeaturesToTrack(frame_gray, mask=mask, maxCorners=50, qualityLevel=0.01, minDistance=30)
        else:
            self.prev_pts = good_new.reshape(-1, 1, 2) if 'good_new' in locals() and len(good_new) > 0 else None
            
        self.prev_gray = frame_gray.copy()
        
        self.motion_smoother.add(motion_magnitude)
        avg_motion = self.motion_smoother.get_average()
        
        # Lowered thresholds for shake detection (pixel displacement per frame)
        if avg_motion > 1.5:
            result["stability"].value = CameraStability.SHAKY
            result["warnings"].append("Camera is shaky")
        elif avg_motion > 0.5:
            result["stability"].value = CameraStability.MODERATE
            
        # 2. Sharpness & Brightness
        sharpness = cv2.Laplacian(frame_gray, cv2.CV_64F).var()
        brightness = np.mean(frame_gray)
        
        # Normalize sharpness to a 0-100 scale roughly
        sharp_score = min(100.0, sharpness / 2.0)
        result["sharpness"].value = sharp_score
        result["brightness"].value = brightness
        
        # 3. Unified Frame Quality Score
        quality = 100.0
        if fps < 15: quality -= 20
        if sharp_score < 30: quality -= 20
        if brightness < 40 or brightness > 220: quality -= 20
        if result["stability"].value == CameraStability.SHAKY: quality -= 15
        
        result["frame_quality_score"] = int(max(0, quality))
        
        if quality < 50:
            result["blocks"].append("Frame quality is too poor")
            
        return result
