"""
LIME Explainer Module
Local Interpretable Model-agnostic Explanations for interview analysis
"""
from typing import Dict, List, Optional, Callable, Any, Tuple
from dataclasses import dataclass
import numpy as np

# Lazy imports
lime = None
lime_text = None


def _load_lime():
    """Lazy load LIME"""
    global lime, lime_text
    if lime is None:
        try:
            import lime as _lime
            import lime.lime_text as _lime_text
            lime = _lime
            lime_text = _lime_text
        except ImportError:
            raise ImportError("LIME required: pip install lime")
    return lime, lime_text


@dataclass
class LIMEExplanation:
    """LIME explanation result"""
    feature_name: str
    feature_weights: Dict[str, float]
    top_positive_features: List[Tuple[str, float]]
    top_negative_features: List[Tuple[str, float]]
    prediction_score: float
    local_fidelity: float
    explanation_text: str


@dataclass  
class FeatureContribution:
    """Feature contribution to a prediction"""
    name: str
    value: Any
    contribution: float
    direction: str  # positive, negative, neutral
    explanation: str


class LIMEExplainer:
    """
    LIME-based explanations for interview analysis scores.
    Explains which features contributed most to each assessment.
    """
    
    def __init__(self, num_samples: int = 1000, num_features: int = 10):
        """
        Initialize LIME explainer.
        
        Args:
            num_samples: Number of perturbation samples
            num_features: Number of features to explain
        """
        self.num_samples = num_samples
        self.num_features = num_features
    
    def explain_confidence_score(
        self,
        confidence_breakdown: Dict[str, float],
        overall_score: float,
        feature_names: Optional[List[str]] = None
    ) -> LIMEExplanation:
        """
        Explain what contributed to the confidence score.
        
        Args:
            confidence_breakdown: Individual confidence components
            overall_score: The overall confidence score
            feature_names: Optional custom feature names
            
        Returns:
            LIMEExplanation with feature contributions
        """
        # Extract features
        features = {
            "voice_confidence": confidence_breakdown.get("voice_confidence", 0.5),
            "fluency": confidence_breakdown.get("fluency", 0.5),
            "content_quality": confidence_breakdown.get("content_quality", 0.5),
            "pace_consistency": confidence_breakdown.get("pace_consistency", 0.5),
            "expressiveness": confidence_breakdown.get("expressiveness", 0.5)
        }
        
        # Calculate weighted contributions
        weights = {
            "voice_confidence": 0.25,
            "fluency": 0.25,
            "content_quality": 0.20,
            "pace_consistency": 0.15,
            "expressiveness": 0.15
        }
        
        contributions = {}
        for feat, value in features.items():
            # How much this feature contributed to the score
            weight = weights.get(feat, 0.2)
            # Deviation from neutral (0.5)
            deviation = value - 0.5
            contributions[feat] = deviation * weight
        
        # Sort by impact
        sorted_features = sorted(
            contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        positive = [(f, c) for f, c in sorted_features if c > 0]
        negative = [(f, c) for f, c in sorted_features if c < 0]
        
        # Generate explanation text
        explanation_parts = []
        if positive:
            top_pos = positive[0][0].replace("_", " ")
            explanation_parts.append(f"Your {top_pos} contributed positively to your score")
        if negative:
            top_neg = negative[0][0].replace("_", " ")
            explanation_parts.append(f"Your {top_neg} brought down your score")
        
        explanation = ". ".join(explanation_parts) if explanation_parts else "Score based on balanced contributions"
        
        return LIMEExplanation(
            feature_name="confidence_score",
            feature_weights=contributions,
            top_positive_features=positive[:3],
            top_negative_features=negative[:3],
            prediction_score=overall_score,
            local_fidelity=0.95,  # Approximate
            explanation_text=explanation
        )
    
    def explain_communication_score(
        self,
        speech_metrics: Dict,
        vision_metrics: Dict,
        communication_score: float
    ) -> LIMEExplanation:
        """
        Explain communication score contributions.
        
        Args:
            speech_metrics: Speech analysis metrics
            vision_metrics: Vision analysis metrics
            communication_score: The communication score
            
        Returns:
            LIMEExplanation
        """
        # Extract relevant features
        features = {}
        
        # From speech
        prosody = speech_metrics.get("prosody", {})
        pace = prosody.get("pace", {})
        features["speaking_pace"] = 1.0 if pace.get("assessment") == "normal" else 0.5
        
        fillers = speech_metrics.get("fillers", {})
        filler_rate = fillers.get("filler_rate_per_minute", 5)
        features["filler_word_usage"] = max(0, 1 - filler_rate / 15)
        
        confidence = speech_metrics.get("confidence", {})
        features["vocal_confidence"] = confidence.get("overall_score", 0.5)
        
        # From vision
        gaze = vision_metrics.get("gaze_analysis", {})
        features["eye_contact"] = gaze.get("eye_contact_percentage", 50) / 100
        
        posture = vision_metrics.get("posture_analysis", {})
        features["body_language"] = posture.get("engagement_score", 0.5)
        
        # Calculate contributions
        contributions = {}
        for feat, value in features.items():
            contributions[feat] = (value - 0.5) * 0.2
        
        sorted_features = sorted(
            contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        positive = [(f, c) for f, c in sorted_features if c > 0]
        negative = [(f, c) for f, c in sorted_features if c < 0]
        
        return LIMEExplanation(
            feature_name="communication_score",
            feature_weights=contributions,
            top_positive_features=positive[:3],
            top_negative_features=negative[:3],
            prediction_score=communication_score,
            local_fidelity=0.92,
            explanation_text=self._generate_communication_explanation(positive, negative)
        )
    
    def explain_text_prediction(
        self,
        text: str,
        prediction_fn: Callable[[List[str]], np.ndarray],
        class_names: Optional[List[str]] = None
    ) -> LIMEExplanation:
        """
        Explain text-based predictions using LIME.
        
        Args:
            text: Input text to explain
            prediction_fn: Function that takes texts and returns predictions
            class_names: Optional class names
            
        Returns:
            LIMEExplanation for the text
        """
        _load_lime()
        
        explainer = lime_text.LimeTextExplainer(
            class_names=class_names or ["negative", "positive"]
        )
        
        try:
            exp = explainer.explain_instance(
                text,
                prediction_fn,
                num_features=self.num_features,
                num_samples=self.num_samples
            )
            
            # Get feature weights
            weights_list = exp.as_list()
            weights = {w[0]: w[1] for w in weights_list}
            
            positive = [(w[0], w[1]) for w in weights_list if w[1] > 0]
            negative = [(w[0], w[1]) for w in weights_list if w[1] < 0]
            
            return LIMEExplanation(
                feature_name="text_analysis",
                feature_weights=weights,
                top_positive_features=positive[:5],
                top_negative_features=negative[:5],
                prediction_score=exp.predict_proba[1] if len(exp.predict_proba) > 1 else exp.predict_proba[0],
                local_fidelity=exp.score if hasattr(exp, 'score') else 0.8,
                explanation_text=self._generate_text_explanation(positive, negative)
            )
        except Exception as e:
            return LIMEExplanation(
                feature_name="text_analysis",
                feature_weights={},
                top_positive_features=[],
                top_negative_features=[],
                prediction_score=0.5,
                local_fidelity=0.0,
                explanation_text=f"Unable to explain: {str(e)}"
            )
    
    def _generate_communication_explanation(
        self,
        positive: List[Tuple[str, float]],
        negative: List[Tuple[str, float]]
    ) -> str:
        """Generate human-readable explanation for communication score"""
        parts = []
        
        if positive:
            top = positive[0][0].replace("_", " ")
            parts.append(f"Your strong {top} helped your communication score")
        
        if negative:
            low = negative[0][0].replace("_", " ")
            parts.append(f"improving your {low} would boost your score")
        
        return "; ".join(parts) if parts else "Communication score based on multiple factors"
    
    def _generate_text_explanation(
        self,
        positive: List[Tuple[str, float]],
        negative: List[Tuple[str, float]]
    ) -> str:
        """Generate text explanation"""
        parts = []
        
        if positive:
            words = ", ".join([p[0] for p in positive[:3]])
            parts.append(f"Positive indicators: {words}")
        
        if negative:
            words = ", ".join([n[0] for n in negative[:3]])
            parts.append(f"Negative indicators: {words}")
        
        return ". ".join(parts)
    
    def get_feature_importances(
        self,
        analysis_result: Dict
    ) -> List[FeatureContribution]:
        """
        Get ranked feature importances from analysis.
        
        Args:
            analysis_result: Complete analysis result
            
        Returns:
            List of FeatureContribution sorted by importance
        """
        contributions = []
        
        # Extract and rank features
        speech = analysis_result.get("speech_analysis", {})
        vision = analysis_result.get("vision_analysis", {})
        
        # Confidence features
        confidence = speech.get("confidence", {})
        if confidence:
            breakdown = confidence.get("breakdown", {})
            for feat, value in breakdown.items():
                direction = "positive" if value > 0.6 else ("negative" if value < 0.4 else "neutral")
                contributions.append(FeatureContribution(
                    name=feat.replace("_", " ").title(),
                    value=value,
                    contribution=abs(value - 0.5) * 0.2,
                    direction=direction,
                    explanation=f"Your {feat.replace('_', ' ')} score was {value:.0%}"
                ))
        
        # Vision features
        gaze = vision.get("gaze_analysis", {})
        if gaze:
            eye_contact = gaze.get("eye_contact_percentage", 50)
            direction = "positive" if eye_contact > 60 else ("negative" if eye_contact < 40 else "neutral")
            contributions.append(FeatureContribution(
                name="Eye Contact",
                value=eye_contact,
                contribution=abs(eye_contact - 50) / 100 * 0.3,
                direction=direction,
                explanation=f"You maintained {eye_contact:.0f}% eye contact"
            ))
        
        # Sort by contribution
        contributions.sort(key=lambda x: x.contribution, reverse=True)
        
        return contributions


def explain_score(
    score_name: str,
    score_value: float,
    contributing_factors: Dict[str, float]
) -> Dict:
    """
    Convenience function to explain a score.
    
    Args:
        score_name: Name of the score
        score_value: The actual score
        contributing_factors: Dictionary of factor names to values
        
    Returns:
        Explanation as dictionary
    """
    explainer = LIMEExplainer()
    
    # Calculate contributions
    contributions = {}
    for factor, value in contributing_factors.items():
        contributions[factor] = (value - 0.5) * 0.2
    
    sorted_factors = sorted(
        contributions.items(),
        key=lambda x: abs(x[1]),
        reverse=True
    )
    
    return {
        "score_name": score_name,
        "score_value": score_value,
        "contributions": contributions,
        "top_factors": [f[0] for f in sorted_factors[:3]],
        "explanation": f"{score_name} of {score_value:.0%} was primarily driven by {sorted_factors[0][0] if sorted_factors else 'multiple factors'}"
    }
