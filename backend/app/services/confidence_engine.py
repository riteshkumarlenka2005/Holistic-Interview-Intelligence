"""
Confidence Engine.
Aggregates multimodal signals (verbal and non-verbal) into a unified Confidence Score.
Classifies the score into Confidence Bands for the Orchestrator to adapt difficulty.
"""
from typing import Dict, Any


class ConfidenceEngine:
    
    @staticmethod
    def calculate_confidence(
        speech_fluency_score: float,
        eye_contact_percent: float,
        head_stability_score: float,
        facial_engagement_score: float
    ) -> Dict[str, Any]:
        """
        Fuses the 4 core metrics into a single confidence score (0-100).
        Formula:
          Speech Fluency (35%)
          Eye Contact (35%)
          Head Stability (15%)
          Facial Engagement (15%) - Replacing smile
        """
        score = (
            (speech_fluency_score * 0.35) +
            (eye_contact_percent * 0.35) +
            (head_stability_score * 0.15) +
            (facial_engagement_score * 0.15)
        )
        
        score = max(0.0, min(100.0, score))
        
        # Determine Confidence Band
        if score <= 40:
            band = "Low"
            modifier_delta = -1
        elif score <= 65:
            band = "Moderate"
            modifier_delta = 0
        elif score <= 85:
            band = "Good"
            modifier_delta = 0
        else:
            band = "High"
            modifier_delta = +1

        return {
            "confidence_score": round(score, 1),
            "confidence_band": band,
            "difficulty_modifier_delta": modifier_delta,
            "components": {
                "speech_fluency": speech_fluency_score,
                "eye_contact": eye_contact_percent,
                "head_stability": head_stability_score,
                "facial_engagement": facial_engagement_score
            }
        }
