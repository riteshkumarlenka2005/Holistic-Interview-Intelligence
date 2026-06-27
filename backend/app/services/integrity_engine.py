"""
Integrity Engine — Fairness and Cheating Detection.

Tracks suspicious behavior throughout the interview session.

Monitored events:
    tab_switch          → Candidate switched browser tab          (-2 pts)
    window_blur         → Browser window lost focus               (-3 pts)
    multiple_faces      → More than one face detected in frame    (-15 pts)
    distraction_event   → Looking away for > 8 seconds           (-10 pts)

Integrity Score: starts at 100, deductions applied per event.
Minimum score: 0.

The IntegrityEngine is purely arithmetic — no AI models used.
"""
from typing import List, Dict, Any
from app.models.integrity import IntegrityEvent


# Deduction map — event_type → points deducted per occurrence
DEDUCTION_MAP: Dict[str, int] = {
    "tab_switch":        2,
    "window_blur":       3,
    "multiple_faces":   15,
    "distraction_event": 10,
}


class IntegrityEngine:

    def calculate_score(self, events: List[IntegrityEvent]) -> int:
        """
        Computes the Integrity Score for a session.

        Starts at 100, applies deductions per event.
        Returns final score (minimum 0).
        """
        score = 100
        for event in events:
            deduction = DEDUCTION_MAP.get(event.event_type, 0)
            score -= deduction
        return max(0, score)

    def generate_summary(self, events: List[IntegrityEvent]) -> Dict[str, Any]:
        """
        Generates a human-readable summary of all integrity events.

        Returns:
            integrity_score (int)
            tab_switches    (int)
            window_blurs    (int)
            multiple_faces  (int)
            distractions    (int)
            total_events    (int)
            risk_level      ("Low" | "Medium" | "High")
        """
        summary = {
            "tab_switches":    0,
            "window_blurs":    0,
            "multiple_faces":  0,
            "distractions":    0,
        }

        for event in events:
            t = event.event_type
            if t == "tab_switch":
                summary["tab_switches"] += 1
            elif t == "window_blur":
                summary["window_blurs"] += 1
            elif t == "multiple_faces":
                summary["multiple_faces"] += 1
            elif t == "distraction_event":
                summary["distractions"] += 1

        score = self.calculate_score(events)
        total = len(events)

        if score >= 80:
            risk_level = "Low"
        elif score >= 50:
            risk_level = "Medium"
        else:
            risk_level = "High"

        return {
            "integrity_score": score,
            "tab_switches":    summary["tab_switches"],
            "window_blurs":    summary["window_blurs"],
            "multiple_faces":  summary["multiple_faces"],
            "distractions":    summary["distractions"],
            "total_events":    total,
            "risk_level":      risk_level,
        }
