import time

class TriggerEngine:
    def __init__(self):
        self.last_face_count = 0
        self.last_periodic_check = time.time()
        self.last_face_area = None
        self.time_face_lost = None
        
    def evaluate(self, current_face_count: int, is_new_candidate: bool, current_face_area: float) -> list:
        triggers = []
        now = time.time()
        
        # 1. FACE_APPEARED
        if self.last_face_count == 0 and current_face_count >= 1:
            triggers.append("FACE_APPEARED")
            
        # 2. MULTIPLE_FACES
        if current_face_count > 1:
            triggers.append("MULTIPLE_FACES")
            
        # 3. FACE_SWAP
        if is_new_candidate and self.last_face_count >= 1 and current_face_count >= 1:
            triggers.append("FACE_SWAP")
            
        # 4. LONG_FACE_LOSS
        if current_face_count == 0:
            if self.time_face_lost is None:
                self.time_face_lost = now
        else:
            if self.time_face_lost is not None:
                lost_duration = now - self.time_face_lost
                if lost_duration > 10.0:
                    triggers.append("LONG_FACE_LOSS")
                self.time_face_lost = None
                
        # 5. SUDDEN_SIZE_CHANGE
        if current_face_area is not None and self.last_face_area is not None:
            # Change relative to the last area
            change_ratio = abs(current_face_area - self.last_face_area) / (self.last_face_area + 1e-6)
            if change_ratio > 0.30: # 30% sudden change
                triggers.append("SUDDEN_SIZE_CHANGE")
                
        if current_face_area is not None:
            self.last_face_area = current_face_area
            
        # 6. PERIODIC_CHECK
        if now - self.last_periodic_check > 300.0: # 5 minutes
            triggers.append("PERIODIC_CHECK")
            self.last_periodic_check = now
            
        self.last_face_count = current_face_count
        return triggers
