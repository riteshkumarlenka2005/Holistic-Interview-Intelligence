from .utils import RollingAverage
import time

class BehaviorAnalyzer:
    def __init__(self):
        self.head_movement_freq = RollingAverage(60) # 60 second window
        self.last_pitch = 0
        self.last_yaw = 0
        self.last_update = time.time()
        
    def process(self, pitch: float, yaw: float, gaze_dir: str) -> dict:
        now = time.time()
        dt = now - self.last_update
        
        # Calculate velocity of head movement
        dpitch = abs(pitch - self.last_pitch)
        dyaw = abs(yaw - self.last_yaw)
        movement_speed = (dpitch + dyaw) / max(0.1, dt)
        
        self.head_movement_freq.add(movement_speed)
        
        self.last_pitch = pitch
        self.last_yaw = yaw
        self.last_update = now
        
        result = {
            "head_movement_velocity": self.head_movement_freq.get_average(),
            "fidgeting": False,
            "warnings": []
        }
        
        # If the average velocity is high, they are moving a lot
        if result["head_movement_velocity"] > 50.0:
            result["fidgeting"] = True
            result["warnings"].append("High head movement (fidgeting)")
            
        return result
