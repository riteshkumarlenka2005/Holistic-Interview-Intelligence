from ultralytics import YOLO
import time
from .models import ConfidentValue
from .utils import RollingAverage

class BackgroundAnalyzer:
    def __init__(self):
        # We use YOLOv8 Nano for extremely fast, real-time background analysis
        # It automatically downloads the model weights if not found locally
        self.model = YOLO("yolov8n.pt")
        self.clutter_score_smoother = RollingAverage(window_size_seconds=2.0)
        
        # Object impact weights for clutter scoring
        self.impact_weights = {
            # Low Impact
            "chair": 1,
            "dining table": 1,
            "potted plant": 1,
            "book": 1,
            "bed": 2,
            # Medium Impact
            "laptop": 3,
            "monitor": 3,
            "cell phone": 4,
            "bottle": 2,
            # High Impact
            "person": 0,  # Person is handled by face_validator for blocks, but adds to clutter if > 1
            "tv": 5,
            "dog": 6,
            "cat": 6
        }

    def process(self, frame, face_bbox: tuple) -> dict:
        """
        frame: raw BGR image
        face_bbox: (x_min, y_min, x_max, y_max) pixel coordinates of the candidate's face
        """
        # Run YOLO inference
        # We set verbose=False to keep the terminal clean
        results = self.model(frame, verbose=False)
        
        raw_clutter_score = 0.0
        confidence_sum = 0.0
        objects_counted = 0
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                class_name = self.model.names[cls_id]
                
                # Check if this object is inside the face bounding box (e.g. it's the candidate)
                x1, y1, x2, y2 = box.xyxy[0]
                is_candidate = False
                if class_name == "person" and face_bbox:
                    fx1, fy1, fx2, fy2 = face_bbox
                    # Simple IoU / overlap check to ignore the main candidate
                    overlap_x = max(0, min(x2, fx2) - max(x1, fx1))
                    overlap_y = max(0, min(y2, fy2) - max(y1, fy1))
                    overlap_area = overlap_x * overlap_y
                    if overlap_area > 0.5 * ((x2-x1)*(y2-y1)):
                        is_candidate = True
                        
                if not is_candidate:
                    weight = self.impact_weights.get(class_name, 1)  # Default weight 1 for unknown objects
                    raw_clutter_score += (weight * conf)
                    confidence_sum += conf
                    objects_counted += 1
        
        self.clutter_score_smoother.add(raw_clutter_score)
        avg_clutter = self.clutter_score_smoother.get_average()
        
        overall_confidence = (confidence_sum / objects_counted * 100) if objects_counted > 0 else 100.0
        
        status = "CLEAN"
        if avg_clutter > 10.0:
            status = "MESSY"
        elif avg_clutter > 5.0:
            status = "MODERATE"
            
        return {
            "status": status,
            "clutter_score": ConfidentValue(value=status, confidence=overall_confidence),
            "warnings": ["Background is cluttered"] if avg_clutter > 10.0 else []
        }
