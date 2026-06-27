import math

class CandidateTracker:
    def __init__(self):
        self.candidate_id = "CANDIDATE_01"
        self.last_bbox = None
        self.frames_lost = 0
        
    def _calculate_iou(self, boxA, boxB):
        # box: (x_min, y_min, x_max, y_max)
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])
        
        interArea = max(0, xB - xA) * max(0, yB - yA)
        if interArea == 0:
            return 0.0
            
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])
        
        iou = interArea / float(boxAArea + boxBArea - interArea)
        return iou
        
    def _calculate_distance(self, boxA, boxB):
        center_A = ((boxA[0] + boxA[2]) / 2, (boxA[1] + boxA[3]) / 2)
        center_B = ((boxB[0] + boxB[2]) / 2, (boxB[1] + boxB[3]) / 2)
        return math.sqrt((center_A[0] - center_B[0])**2 + (center_A[1] - center_B[1])**2)

    def track(self, detected_faces_bboxes: list) -> tuple:
        """
        Returns (candidate_bbox, is_new_candidate, list_of_secondary_bboxes)
        """
        if not detected_faces_bboxes:
            self.frames_lost += 1
            return None, False, []
            
        # If we have no candidate tracked yet, lock onto the largest face
        if self.last_bbox is None:
            largest_box = max(detected_faces_bboxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]))
            self.last_bbox = largest_box
            secondary_faces = [b for b in detected_faces_bboxes if b != largest_box]
            return largest_box, True, secondary_faces
            
        # Match current faces to the last known candidate bounding box
        best_match = None
        best_score = -float('inf')
        
        for box in detected_faces_bboxes:
            iou = self._calculate_iou(self.last_bbox, box)
            dist = self._calculate_distance(self.last_bbox, box)
            
            # Score = IoU (higher is better) - Distance penalty
            # A face in the exact same spot will have high IoU and low distance
            score = (iou * 100) - (dist * 0.1)
            
            if score > best_score:
                best_score = score
                best_match = box
                
        # If the best match is terrible (IoU essentially 0 and distance huge), 
        # it means the candidate completely moved or swapped.
        is_new_candidate = False
        if best_score < -50: # Threshold for completely lost track
            is_new_candidate = True
            
        self.last_bbox = best_match
        self.frames_lost = 0
        
        secondary_faces = [b for b in detected_faces_bboxes if b != best_match]
        return best_match, is_new_candidate, secondary_faces
