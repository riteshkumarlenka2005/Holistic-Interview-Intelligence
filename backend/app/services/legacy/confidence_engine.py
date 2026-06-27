"""
Confidence Engine — Multimodal Confidence Scoring.

Fuses four signals from Speech and Vision AI into a unified Confidence Score.

Formula (as per blueprint):
    Speech Fluency    → 40%
    Eye Contact       → 35%
    Head Stability    → 15%
    Facial Engagement → 10%

Confidence Bands:
    0-40  → Low
    41-65 → Moderate
    66-85 → Good
    86-100→ High
"""
from typing import Dict, Any


class ConfidenceEngine:

    @staticmethod
    def calculate_confidence(
        speech_fluency_score: float,
        eye_contact_percent: float,
        head_stability_score: float,
        facial_engagement_score: float,
    ) -> Dict[str, Any]:
        """
        Fuses 4 core metrics into a single Confidence Score (0-100).

        Input ranges: all metrics expected 0-100.

        Returns:
            confidence_score (float 0-100)
            confidence_band  ("Low" | "Moderate" | "Good" | "High")
            difficulty_modifier_delta (-1 | 0 | +1) — for InterviewBrain
            components (dict of all input signals)
        """
        # Clamp all inputs to valid range
        def clamp(v):
            return max(0.0, min(100.0, float(v)))

        speech    = clamp(speech_fluency_score)
        eye       = clamp(eye_contact_percent)
        stability = clamp(head_stability_score)
        engagement= clamp(facial_engagement_score)

        # Weighted fusion — exact blueprint weights
        score = (
            speech     * 0.40 +
            eye        * 0.35 +
            stability  * 0.15 +
            engagement * 0.10
        )
        score = max(0.0, min(100.0, score))

        # Confidence Band classification
        if score <= 40:
            band = "Low"
            modifier_delta = -1    # InterviewBrain should reduce difficulty
        elif score <= 65:
            band = "Moderate"
            modifier_delta = 0
        elif score <= 85:
            band = "Good"
            modifier_delta = 0
        else:
            band = "High"
            modifier_delta = +1    # InterviewBrain should increase difficulty

        return {
            "confidence_score": round(score, 1),
            "confidence_band": band,
            "difficulty_modifier_delta": modifier_delta,
            "components": {
                "speech_fluency":     round(speech, 1),
                "eye_contact":        round(eye, 1),
                "head_stability":     round(stability, 1),
                "facial_engagement":  round(engagement, 1),
            },
        }
