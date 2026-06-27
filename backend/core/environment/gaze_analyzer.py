from .types import GazeDirection
from .models import ConfidentValue

class GazeAnalyzer:
    def process(self, horiz_ratio: float, vert_ratio: float) -> dict:
        direction = GazeDirection.CENTER
        confidence = 98.0
        
        # Widened the 'CENTER' deadzone so slight head movements don't trigger it
        if horiz_ratio < 0.32:
            direction = GazeDirection.RIGHT
        elif horiz_ratio > 0.68:
            direction = GazeDirection.LEFT
        elif vert_ratio < 0.28:
            direction = GazeDirection.UP
        elif vert_ratio > 0.72:
            direction = GazeDirection.DOWN
            
        eye_contact = (direction == GazeDirection.CENTER)
        
        # If the ratio is very close to the threshold, confidence drops
        if not eye_contact:
            if 0.30 <= horiz_ratio <= 0.34 or 0.66 <= horiz_ratio <= 0.70:
                confidence = 65.0
            if 0.26 <= vert_ratio <= 0.30 or 0.70 <= vert_ratio <= 0.74:
                confidence = 65.0
                
        result = {
            "eye_contact": ConfidentValue(value=eye_contact, confidence=confidence),
            "direction": ConfidentValue(value=direction, confidence=confidence),
            "warnings": []
        }
        
        if not eye_contact:
            result["warnings"].append(f"Gaze shifted {direction.value}")
            
        return result
