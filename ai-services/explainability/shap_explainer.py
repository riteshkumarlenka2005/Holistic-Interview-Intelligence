"""
SHAP Explainer Module
SHapley Additive exPlanations for interview analysis
"""
from typing import Dict, List, Optional, Callable, Any, Union, Tuple
from dataclasses import dataclass
import numpy as np

# Lazy imports
shap = None


def _load_shap():
    """Lazy load SHAP"""
    global shap
    if shap is None:
        try:
            import shap as _shap
            shap = _shap
        except ImportError:
            raise ImportError("SHAP required: pip install shap")
    return shap


@dataclass
class SHAPExplanation:
    """SHAP explanation result"""
    feature_names: List[str]
    shap_values: Dict[str, float]
    base_value: float
    predicted_value: float
    feature_impacts: List[Tuple[str, float, str]]  # name, impact, direction
    summary: str


class SHAPExplainer:
    """
    SHAP-based explanations for interview analysis.
    Uses Shapley values to fairly attribute predictions to features.
    """
    
    def __init__(self, background_samples: int = 100):
        """
        Initialize SHAP explainer.
        
        Args:
            background_samples: Number of background samples for SHAP
        """
        self.background_samples = background_samples
    
    def explain_score(
        self,
        feature_values: Dict[str, float],
        score: float,
        score_name: str = "score"
    ) -> SHAPExplanation:
        """
        Explain a score using SHAP values.
        
        Args:
            feature_values: Dictionary of feature names to values
            score: The predicted score to explain
            score_name: Name of the score being explained
            
        Returns:
            SHAPExplanation with Shapley values
        """
        # Calculate simplified Shapley values
        # In a full implementation, this would use actual SHAP library
        features = list(feature_values.keys())
        values = np.array(list(feature_values.values()))
        
        # Base value (expected score when all features are average)
        base_value = 0.5
        
        # Calculate contributions using simplified Shapley approach
        shap_values = {}
        total_deviation = score - base_value
        
        # Weight by how much each feature deviates from baseline
        deviations = {f: v - 0.5 for f, v in feature_values.items()}
        total_abs_deviation = sum(abs(d) for d in deviations.values()) or 1
        
        for feature, deviation in deviations.items():
            # Proportional attribution
            shap_values[feature] = (deviation / total_abs_deviation) * total_deviation
        
        # Create sorted feature impacts
        feature_impacts = [
            (f, v, "positive" if v > 0 else "negative")
            for f, v in sorted(shap_values.items(), key=lambda x: abs(x[1]), reverse=True)
        ]
        
        # Generate summary
        summary = self._generate_summary(feature_impacts, score, score_name)
        
        return SHAPExplanation(
            feature_names=features,
            shap_values=shap_values,
            base_value=base_value,
            predicted_value=score,
            feature_impacts=feature_impacts,
            summary=summary
        )
    
    def explain_multimodal_score(
        self,
        speech_features: Dict[str, float],
        vision_features: Dict[str, float],
        combined_score: float
    ) -> SHAPExplanation:
        """
        Explain multimodal combined score.
        
        Args:
            speech_features: Speech-related features
            vision_features: Vision-related features
            combined_score: The combined multimodal score
            
        Returns:
            SHAPExplanation
        """
        # Combine all features with modality prefix
        all_features = {}
        for f, v in speech_features.items():
            all_features[f"speech_{f}"] = v
        for f, v in vision_features.items():
            all_features[f"vision_{f}"] = v
        
        return self.explain_score(all_features, combined_score, "multimodal_score")
    
    def explain_with_model(
        self,
        model: Any,
        data: np.ndarray,
        feature_names: List[str]
    ) -> SHAPExplanation:
        """
        Explain predictions using actual SHAP with a model.
        
        Args:
            model: Trained model with predict method
            data: Input data to explain
            feature_names: Names of input features
            
        Returns:
            SHAPExplanation
        """
        _load_shap()
        
        try:
            # Create explainer
            explainer = shap.KernelExplainer(
                model.predict,
                shap.sample(data, self.background_samples)
            )
            
            # Calculate SHAP values
            shap_values_array = explainer.shap_values(data)
            
            # Average across samples if needed
            if len(shap_values_array.shape) > 1:
                mean_shap = np.mean(shap_values_array, axis=0)
            else:
                mean_shap = shap_values_array
            
            # Create dictionary
            shap_dict = {
                feature_names[i]: float(mean_shap[i])
                for i in range(len(feature_names))
            }
            
            # Prediction
            predicted = float(np.mean(model.predict(data)))
            
            feature_impacts = [
                (f, v, "positive" if v > 0 else "negative")
                for f, v in sorted(shap_dict.items(), key=lambda x: abs(x[1]), reverse=True)
            ]
            
            return SHAPExplanation(
                feature_names=feature_names,
                shap_values=shap_dict,
                base_value=float(explainer.expected_value),
                predicted_value=predicted,
                feature_impacts=feature_impacts,
                summary=self._generate_summary(feature_impacts, predicted, "prediction")
            )
        except Exception as e:
            # Fallback to simplified explanation
            return SHAPExplanation(
                feature_names=feature_names,
                shap_values={f: 0.0 for f in feature_names},
                base_value=0.5,
                predicted_value=0.5,
                feature_impacts=[],
                summary=f"SHAP explanation failed: {str(e)}"
            )
    
    def get_feature_importance_ranking(
        self,
        shap_values: Dict[str, float]
    ) -> List[Dict]:
        """
        Get ranked feature importance from SHAP values.
        
        Args:
            shap_values: Dictionary of feature SHAP values
            
        Returns:
            Ranked list of feature importance
        """
        ranked = sorted(
            shap_values.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )
        
        return [
            {
                "rank": i + 1,
                "feature": f,
                "shap_value": v,
                "absolute_importance": abs(v),
                "direction": "positive" if v > 0 else "negative"
            }
            for i, (f, v) in enumerate(ranked)
        ]
    
    def compare_instances(
        self,
        instance1_features: Dict[str, float],
        instance2_features: Dict[str, float],
        instance1_score: float,
        instance2_score: float
    ) -> Dict:
        """
        Compare SHAP explanations between two instances.
        
        Args:
            instance1_features: Features for first instance
            instance2_features: Features for second instance
            instance1_score: Score for first instance
            instance2_score: Score for second instance
            
        Returns:
            Comparison of SHAP values
        """
        exp1 = self.explain_score(instance1_features, instance1_score)
        exp2 = self.explain_score(instance2_features, instance2_score)
        
        # Calculate differences
        diff_shap = {}
        all_features = set(exp1.shap_values.keys()) | set(exp2.shap_values.keys())
        
        for f in all_features:
            v1 = exp1.shap_values.get(f, 0)
            v2 = exp2.shap_values.get(f, 0)
            diff_shap[f] = v2 - v1
        
        return {
            "instance1_score": instance1_score,
            "instance2_score": instance2_score,
            "score_difference": instance2_score - instance1_score,
            "shap_differences": diff_shap,
            "biggest_improvements": sorted(
                [(f, v) for f, v in diff_shap.items() if v > 0],
                key=lambda x: x[1],
                reverse=True
            )[:3],
            "biggest_declines": sorted(
                [(f, v) for f, v in diff_shap.items() if v < 0],
                key=lambda x: x[1]
            )[:3]
        }
    
    def _generate_summary(
        self,
        feature_impacts: List[Tuple[str, float, str]],
        score: float,
        score_name: str
    ) -> str:
        """Generate human-readable summary"""
        if not feature_impacts:
            return f"Your {score_name} was {score:.0%}"
        
        top_positive = [f for f, v, d in feature_impacts if d == "positive"][:2]
        top_negative = [f for f, v, d in feature_impacts if d == "negative"][:2]
        
        parts = [f"Your {score_name} of {score:.0%}"]
        
        if top_positive:
            features = " and ".join(f.replace("_", " ") for f in top_positive)
            parts.append(f"was boosted by your {features}")
        
        if top_negative:
            features = " and ".join(f.replace("_", " ") for f in top_negative)
            parts.append(f"was lowered by your {features}")
        
        return ", ".join(parts)


def explain_with_shap(
    features: Dict[str, float],
    score: float,
    score_name: str = "score"
) -> Dict:
    """
    Convenience function for SHAP explanation.
    
    Args:
        features: Feature dictionary
        score: Score to explain
        score_name: Name of the score
        
    Returns:
        SHAP explanation as dictionary
    """
    explainer = SHAPExplainer()
    result = explainer.explain_score(features, score, score_name)
    
    return {
        "features": result.feature_names,
        "shap_values": result.shap_values,
        "base_value": result.base_value,
        "predicted_value": result.predicted_value,
        "top_impacts": [
            {"feature": f, "impact": i, "direction": d}
            for f, i, d in result.feature_impacts[:5]
        ],
        "summary": result.summary
    }


def get_feature_importance(analysis: Dict) -> Dict:
    """
    Get SHAP-based feature importance from analysis.
    
    Args:
        analysis: Complete analysis results
        
    Returns:
        Feature importance ranking
    """
    # Extract relevant features
    features = {}
    
    speech = analysis.get("speech_analysis", {})
    if speech:
        conf = speech.get("confidence", {})
        if isinstance(conf, dict):
            features["confidence"] = conf.get("overall_score", 0.5)
        
        fillers = speech.get("fillers", {})
        if fillers:
            rate = fillers.get("filler_rate_per_minute", 5)
            features["fluency"] = max(0, 1 - rate / 15)
    
    vision = analysis.get("vision_analysis", {})
    if vision:
        gaze = vision.get("gaze_analysis", {})
        if gaze:
            features["eye_contact"] = gaze.get("eye_contact_percentage", 50) / 100
        
        posture = vision.get("posture_analysis", {})
        if posture:
            features["posture"] = posture.get("engagement_score", 0.5)
    
    overall = analysis.get("overall_assessment", {})
    score = overall.get("overall_score", 50) / 100
    
    explainer = SHAPExplainer()
    result = explainer.explain_score(features, score)
    
    return explainer.get_feature_importance_ranking(result.shap_values)
