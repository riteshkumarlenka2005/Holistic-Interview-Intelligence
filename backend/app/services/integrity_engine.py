from typing import List
from app.models.integrity import IntegrityEvent

class IntegrityEngine:
    def __init__(self):
        # Weights for different integrity deductions
        self.deductions = {
            "tab_switch": 2,
            "window_blur": 3,
            "distraction_event": 10,
            "multiple_faces": 15
        }

    def calculate_score(self, events: List[IntegrityEvent]) -> int:
        """
        Calculates the integrity score starting from 100 and deducting points
        based on the frequency and severity of events.
        """
        score = 100
        
        for event in events:
            deduction = self.deductions.get(event.event_type, 0)
            score -= deduction
            
        # Ensure score doesn't drop below 0
        return max(0, score)
    
    def generate_summary(self, events: List[IntegrityEvent]) -> dict:
        """
        Generates a summary of the events for the report.
        """
        summary = {
            "tab_switches": 0,
            "window_blurs": 0,
            "distractions": 0,
            "multiple_faces": 0,
        }
        
        for event in events:
            if event.event_type == "tab_switch":
                summary["tab_switches"] += 1
            elif event.event_type == "window_blur":
                summary["window_blurs"] += 1
            elif event.event_type == "distraction_event":
                summary["distractions"] += 1
            elif event.event_type == "multiple_faces":
                summary["multiple_faces"] += 1
                
        return summary
