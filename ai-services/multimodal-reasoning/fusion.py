"""
Multimodal Fusion Module
Combines speech and vision analysis results with weighted integration
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class FusionWeights:
    """Configurable weights for modality fusion"""
    speech_weight: float = 0.5
    vision_weight: float = 0.5
    content_weight: float = 0.4  # Within speech
    prosody_weight: float = 0.3  # Within speech
    fluency_weight: float = 0.3  # Within speech
    gaze_weight: float = 0.35  # Within vision
    posture_weight: float = 0.30  # Within vision
    expression_weight: float = 0.35  # Within vision


@dataclass
class CongruenceResult:
    """Result of congruence analysis between modalities"""
    is_congruent: bool
    congruence_score: float  # 0-1
    incongruent_areas: List[Dict]
    interpretation: str


@dataclass
class FusionResult:
    """Complete multimodal fusion result"""
    combined_confidence: float
    communication_score: float
    presence_score: float
    engagement_score: float
    authenticity_score: float
    congruence: CongruenceResult
    modality_contributions: Dict[str, float]
    integrated_assessment: str
    key_insights: List[str]


class MultimodalFusion:
    """
    Fuses speech and vision analysis results.
    Detects congruence/incongruence between modalities.
    """
    
    def __init__(self, weights: Optional[FusionWeights] = None):
        """
        Initialize fusion module.
        
        Args:
            weights: Custom fusion weights or None for defaults
        """
        self.weights = weights or FusionWeights()
    
    def fuse(
        self,
        speech_analysis: Dict,
        vision_analysis: Dict,
        content_analysis: Optional[Dict] = None
    ) -> FusionResult:
        """
        Fuse speech and vision analysis results.
        
        Args:
            speech_analysis: Results from speech analysis pipeline
            vision_analysis: Results from vision analysis pipeline
            content_analysis: Optional content/answer quality analysis
            
        Returns:
            FusionResult with combined metrics
        """
        # Extract key metrics from speech
        speech_confidence = self._extract_speech_confidence(speech_analysis)
        
        # Extract key metrics from vision
        vision_confidence = self._extract_vision_confidence(vision_analysis)
        
        # Calculate combined confidence
        combined_confidence = (
            speech_confidence * self.weights.speech_weight +
            vision_confidence * self.weights.vision_weight
        )
        
        # Calculate dimension scores
        communication_score = self._calculate_communication_score(
            speech_analysis, vision_analysis
        )
        presence_score = self._calculate_presence_score(vision_analysis)
        engagement_score = self._calculate_engagement_score(
            speech_analysis, vision_analysis
        )
        
        # Analyze congruence
        congruence = self._analyze_congruence(speech_analysis, vision_analysis)
        
        # Authenticity based on congruence
        authenticity_score = self._calculate_authenticity(congruence, speech_analysis, vision_analysis)
        
        # Modality contributions
        contributions = {
            "speech_verbal": self._get_verbal_contribution(speech_analysis),
            "speech_prosody": self._get_prosody_contribution(speech_analysis),
            "vision_gaze": self._get_gaze_contribution(vision_analysis),
            "vision_posture": self._get_posture_contribution(vision_analysis),
            "vision_expression": self._get_expression_contribution(vision_analysis)
        }
        
        # Generate assessment
        assessment = self._generate_assessment(
            combined_confidence, communication_score,
            presence_score, engagement_score
        )
        
        # Generate key insights
        insights = self._generate_insights(
            speech_analysis, vision_analysis, congruence
        )
        
        return FusionResult(
            combined_confidence=float(combined_confidence),
            communication_score=float(communication_score),
            presence_score=float(presence_score),
            engagement_score=float(engagement_score),
            authenticity_score=float(authenticity_score),
            congruence=congruence,
            modality_contributions=contributions,
            integrated_assessment=assessment,
            key_insights=insights
        )
    
    def _extract_speech_confidence(self, speech: Dict) -> float:
        """Extract overall confidence from speech analysis"""
        confidence = speech.get("confidence", {})
        if isinstance(confidence, dict):
            return confidence.get("overall_score", 0.5)
        return 0.5
    
    def _extract_vision_confidence(self, vision: Dict) -> float:
        """Extract overall confidence from vision analysis"""
        summary = vision.get("summary", {})
        return summary.get("overall_visual_score", 0.5)
    
    def _calculate_communication_score(
        self,
        speech: Dict,
        vision: Dict
    ) -> float:
        """Calculate overall communication effectiveness"""
        scores = []
        
        # Verbal clarity from speech
        prosody = speech.get("prosody", {})
        pace = prosody.get("pace", {})
        if pace.get("assessment") == "normal":
            scores.append(0.85)
        elif pace.get("assessment") in ["slow", "fast"]:
            scores.append(0.55)
        else:
            scores.append(0.5)
        
        # Fluency from speech
        fillers = speech.get("fillers", {})
        filler_rate = fillers.get("filler_rate_per_minute", 5)
        fluency = max(0, 1 - filler_rate / 15)
        scores.append(fluency)
        
        # Visual engagement
        gaze = vision.get("gaze_analysis", {})
        eye_contact = gaze.get("eye_contact_percentage", 50) / 100
        scores.append(eye_contact)
        
        return np.mean(scores)
    
    def _calculate_presence_score(self, vision: Dict) -> float:
        """Calculate professional presence from visual cues"""
        scores = []
        
        # Posture
        posture = vision.get("posture_analysis", {})
        if posture.get("dominant_posture") == "upright":
            scores.append(0.9)
        elif posture.get("dominant_posture") in ["slouching"]:
            scores.append(0.4)
        else:
            scores.append(0.6)
        
        stability = posture.get("posture_stability", 0.5)
        scores.append(stability)
        
        # Engagement from posture
        engagement = posture.get("engagement_score", 0.5)
        scores.append(engagement)
        
        return np.mean(scores)
    
    def _calculate_engagement_score(
        self,
        speech: Dict,
        vision: Dict
    ) -> float:
        """Calculate engagement level"""
        scores = []
        
        # Speech expressiveness
        prosody = speech.get("prosody", {})
        tone = prosody.get("tone", {})
        expressiveness = tone.get("expressiveness", 0.5)
        scores.append(expressiveness)
        
        # Visual engagement
        gaze = vision.get("gaze_analysis", {})
        gaze_stability = gaze.get("gaze_stability", 0.5)
        scores.append(gaze_stability)
        
        # Expression positivity
        expression = vision.get("expression_analysis", {})
        dist = expression.get("expression_distribution", {})
        positive = dist.get("happy", 0) + dist.get("neutral", 0) * 0.5
        scores.append(positive)
        
        return np.mean(scores)
    
    def _analyze_congruence(
        self,
        speech: Dict,
        vision: Dict
    ) -> CongruenceResult:
        """Analyze congruence between speech and visual cues"""
        incongruent_areas = []
        congruence_scores = []
        
        # Check voice confidence vs visual confidence
        speech_confidence = speech.get("confidence", {}).get("overall_score", 0.5)
        vision_summary = vision.get("summary", {})
        visual_score = vision_summary.get("overall_visual_score", 0.5)
        
        confidence_diff = abs(speech_confidence - visual_score)
        if confidence_diff > 0.3:
            incongruent_areas.append({
                "area": "confidence_mismatch",
                "speech": speech_confidence,
                "visual": visual_score,
                "severity": "high" if confidence_diff > 0.4 else "medium"
            })
            congruence_scores.append(1 - confidence_diff)
        else:
            congruence_scores.append(1.0)
        
        # Check speech positivity vs facial expressions
        tone = speech.get("prosody", {}).get("tone", {})
        speech_tone = tone.get("overall", "neutral")
        
        expression = vision.get("expression_analysis", {})
        dominant_expr = expression.get("dominant_expression", "neutral")
        
        # Map tones to expected expressions
        tone_expression_map = {
            "confident": ["happy", "neutral"],
            "neutral": ["neutral", "happy"],
            "hesitant": ["neutral", "fearful", "sad"],
            "nervous": ["fearful", "neutral"]
        }
        
        expected_expressions = tone_expression_map.get(speech_tone, ["neutral"])
        if dominant_expr not in expected_expressions:
            # Check if this is truly incongruent
            dist = expression.get("expression_distribution", {})
            if dist.get(dominant_expr, 0) > 0.4:  # Strong expression mismatch
                incongruent_areas.append({
                    "area": "tone_expression_mismatch",
                    "speech_tone": speech_tone,
                    "facial_expression": dominant_expr,
                    "severity": "medium"
                })
                congruence_scores.append(0.6)
            else:
                congruence_scores.append(0.9)
        else:
            congruence_scores.append(1.0)
        
        # Check for stress indicators with calm speech
        stress_count = expression.get("stress_indicators", 0)
        if stress_count > 3 and speech_tone == "confident":
            incongruent_areas.append({
                "area": "hidden_stress",
                "speech_tone": speech_tone,
                "stress_signals": stress_count,
                "severity": "medium"
            })
            congruence_scores.append(0.5)
        else:
            congruence_scores.append(1.0)
        
        overall_congruence = np.mean(congruence_scores)
        is_congruent = overall_congruence >= 0.7
        
        # Generate interpretation
        if is_congruent:
            interpretation = "Your verbal and non-verbal communication are well aligned."
        elif len(incongruent_areas) == 1:
            area = incongruent_areas[0]["area"]
            if area == "confidence_mismatch":
                interpretation = (
                    "There's a mismatch between your vocal and visual confidence. "
                    "Work on aligning these for more authentic communication."
                )
            elif area == "tone_expression_mismatch":
                interpretation = (
                    "Your facial expression doesn't match your tone of voice. "
                    "This can come across as inauthentic to interviewers."
                )
            else:
                interpretation = (
                    "Some subtle stress signals are visible that don't match "
                    "your vocal delivery. Practice managing visible stress cues."
                )
        else:
            interpretation = (
                "Multiple areas of incongruence were detected between your "
                "verbal and non-verbal communication. Focus on authentic delivery."
            )
        
        return CongruenceResult(
            is_congruent=is_congruent,
            congruence_score=float(overall_congruence),
            incongruent_areas=incongruent_areas,
            interpretation=interpretation
        )
    
    def _calculate_authenticity(
        self,
        congruence: CongruenceResult,
        speech: Dict,
        vision: Dict
    ) -> float:
        """Calculate perceived authenticity score"""
        scores = []
        
        # Congruence contributes significantly
        scores.append(congruence.congruence_score)
        
        # Authentic smiles contribute
        expression = vision.get("expression_analysis", {})
        smile_count = expression.get("authentic_smile_count", 0)
        smile_score = min(1.0, smile_count / 5)  # 5+ smiles = max score
        scores.append(smile_score)
        
        # Emotional consistency
        emotional_congruence = expression.get("emotional_congruence", 0.5)
        scores.append(emotional_congruence)
        
        return np.mean(scores)
    
    def _get_verbal_contribution(self, speech: Dict) -> float:
        """Get verbal content contribution score"""
        confidence = speech.get("confidence", {})
        if isinstance(confidence, dict):
            breakdown = confidence.get("breakdown", {})
            return breakdown.get("content_quality", 0.5)
        return 0.5
    
    def _get_prosody_contribution(self, speech: Dict) -> float:
        """Get prosody contribution score"""
        confidence = speech.get("confidence", {})
        if isinstance(confidence, dict):
            breakdown = confidence.get("breakdown", {})
            return breakdown.get("voice_confidence", 0.5)
        return 0.5
    
    def _get_gaze_contribution(self, vision: Dict) -> float:
        """Get gaze contribution score"""
        gaze = vision.get("gaze_analysis", {})
        return gaze.get("eye_contact_percentage", 50) / 100
    
    def _get_posture_contribution(self, vision: Dict) -> float:
        """Get posture contribution score"""
        posture = vision.get("posture_analysis", {})
        return posture.get("engagement_score", 0.5)
    
    def _get_expression_contribution(self, vision: Dict) -> float:
        """Get expression contribution score"""
        expression = vision.get("expression_analysis", {})
        return expression.get("emotional_congruence", 0.5)
    
    def _generate_assessment(
        self,
        confidence: float,
        communication: float,
        presence: float,
        engagement: float
    ) -> str:
        """Generate overall assessment label"""
        avg_score = np.mean([confidence, communication, presence, engagement])
        
        if avg_score >= 0.80:
            return "Excellent"
        elif avg_score >= 0.65:
            return "Good"
        elif avg_score >= 0.50:
            return "Satisfactory"
        elif avg_score >= 0.35:
            return "Needs Improvement"
        else:
            return "Needs Significant Work"
    
    def _generate_insights(
        self,
        speech: Dict,
        vision: Dict,
        congruence: CongruenceResult
    ) -> List[str]:
        """Generate key insights from fused analysis"""
        insights = []
        
        # Confidence insight
        speech_conf = speech.get("confidence", {}).get("overall_score", 0.5)
        if speech_conf >= 0.75:
            insights.append("Your vocal confidence is strong and projects well")
        elif speech_conf < 0.5:
            insights.append("Work on projecting more vocal confidence")
        
        # Eye contact insight
        gaze = vision.get("gaze_analysis", {})
        eye_contact = gaze.get("eye_contact_percentage", 0)
        if eye_contact < 40:
            insights.append("Eye contact needs improvement - aim for 60-70%")
        elif eye_contact >= 70:
            insights.append("Excellent eye contact maintained throughout")
        
        # Congruence insight
        if not congruence.is_congruent:
            insights.append(
                "Work on aligning verbal and non-verbal cues for authenticity"
            )
        
        # Expression insight
        expression = vision.get("expression_analysis", {})
        if expression.get("authentic_smile_count", 0) >= 3:
            insights.append("Good use of natural, authentic smiles")
        elif expression.get("dominant_expression") == "neutral":
            insights.append("Add more positive expressions to appear engaging")
        
        # Filler words insight
        fillers = speech.get("fillers", {})
        filler_rate = fillers.get("filler_rate_per_minute", 0)
        if filler_rate > 8:
            insights.append(f"Reduce filler words (currently {filler_rate:.1f}/min)")
        
        return insights[:5]  # Top 5 insights


def fuse_modalities(speech_analysis: Dict, vision_analysis: Dict) -> Dict:
    """
    Convenience function for multimodal fusion.
    
    Args:
        speech_analysis: Results from speech analysis
        vision_analysis: Results from vision analysis
        
    Returns:
        Fused analysis as dictionary
    """
    fusion = MultimodalFusion()
    result = fusion.fuse(speech_analysis, vision_analysis)
    
    return {
        "speech_weight": fusion.weights.speech_weight,
        "vision_weight": fusion.weights.vision_weight,
        "combined_confidence": result.combined_confidence,
        "communication_score": result.communication_score,
        "presence_score": result.presence_score,
        "engagement_score": result.engagement_score,
        "authenticity_score": result.authenticity_score,
        "congruence_score": result.congruence.congruence_score,
        "is_congruent": result.congruence.is_congruent,
        "incongruent_areas": result.congruence.incongruent_areas,
        "integrated_scores": {
            "overall": result.combined_confidence,
            "communication": result.communication_score,
            "presence": result.presence_score,
            "engagement": result.engagement_score
        }
    }


def detect_incongruence(speech: Dict, vision: Dict) -> Dict:
    """
    Detect mismatches between speech and visual cues.
    
    Args:
        speech: Speech analysis results
        vision: Vision analysis results
        
    Returns:
        Incongruence detection results
    """
    fusion = MultimodalFusion()
    result = fusion.fuse(speech, vision)
    
    return {
        "incongruence_detected": not result.congruence.is_congruent,
        "areas": result.congruence.incongruent_areas,
        "severity": "high" if result.congruence.congruence_score < 0.5 else (
            "medium" if result.congruence.congruence_score < 0.7 else "none"
        ),
        "interpretation": result.congruence.interpretation
    }
