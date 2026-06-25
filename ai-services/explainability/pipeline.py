"""
Explainability Pipeline
Complete explainability pipeline for interview analysis
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .lime_explainer import (
    LIMEExplainer,
    LIMEExplanation,
    FeatureContribution,
    explain_score
)
from .shap_explainer import (
    SHAPExplainer,
    SHAPExplanation,
    explain_with_shap,
    get_feature_importance
)
from .counterfactual import (
    CounterfactualGenerator,
    CounterfactualExplanation,
    Counterfactual,
    generate_counterfactuals,
    what_if_analysis
)


@dataclass
class ExplainabilityResult:
    """Complete explainability result"""
    lime_explanation: Dict
    shap_explanation: Dict
    counterfactuals: Dict
    feature_importance: List[Dict]
    actionable_insights: List[str]


class ExplainabilityPipeline:
    """
    Complete explainability pipeline combining LIME, SHAP, and counterfactuals.
    """
    
    def __init__(self):
        """Initialize explainability pipeline"""
        self.lime_explainer = LIMEExplainer()
        self.shap_explainer = SHAPExplainer()
        self.cf_generator = CounterfactualGenerator()
    
    def explain(
        self,
        analysis_result: Dict,
        target_score: Optional[float] = None
    ) -> ExplainabilityResult:
        """
        Generate comprehensive explanations for analysis results.
        
        Args:
            analysis_result: Complete interview analysis
            target_score: Optional target score for counterfactuals
            
        Returns:
            Complete ExplainabilityResult
        """
        # Extract features from analysis
        features = self._extract_features(analysis_result)
        
        # Get overall score
        overall = analysis_result.get("overall_assessment", {})
        score = overall.get("overall_score", 50) / 100
        
        # LIME explanation
        lime_result = self.lime_explainer.explain_confidence_score(
            features, score
        )
        lime_dict = {
            "feature_weights": lime_result.feature_weights,
            "top_positive": lime_result.top_positive_features,
            "top_negative": lime_result.top_negative_features,
            "explanation": lime_result.explanation_text
        }
        
        # SHAP explanation
        shap_result = self.shap_explainer.explain_score(
            features, score, "overall_score"
        )
        shap_dict = {
            "shap_values": shap_result.shap_values,
            "base_value": shap_result.base_value,
            "feature_impacts": [
                {"feature": f, "impact": i, "direction": d}
                for f, i, d in shap_result.feature_impacts
            ],
            "summary": shap_result.summary
        }
        
        # Counterfactual explanation
        cf_result = self.cf_generator.generate_counterfactuals(
            features, score, target_score
        )
        cf_dict = {
            "original_score": cf_result.original_score,
            "target_score": cf_result.target_score,
            "changes_needed": cf_result.minimal_changes_needed,
            "effort": cf_result.estimated_effort,
            "improvement_path": cf_result.improvement_path,
            "counterfactuals": [
                {
                    "feature": cf.original_feature,
                    "current": cf.original_value,
                    "suggested": cf.suggested_value,
                    "description": cf.change_description,
                    "improvement": cf.predicted_improvement,
                    "difficulty": cf.difficulty,
                    "actions": cf.action_steps
                }
                for cf in cf_result.counterfactuals
            ]
        }
        
        # Get feature importance ranking
        importance = self.shap_explainer.get_feature_importance_ranking(
            shap_result.shap_values
        )
        
        # Generate actionable insights
        insights = self._generate_insights(
            lime_result, shap_result, cf_result
        )
        
        return ExplainabilityResult(
            lime_explanation=lime_dict,
            shap_explanation=shap_dict,
            counterfactuals=cf_dict,
            feature_importance=importance,
            actionable_insights=insights
        )
    
    def _extract_features(self, analysis: Dict) -> Dict[str, float]:
        """Extract features from analysis result"""
        features = {}
        
        # From speech analysis
        speech = analysis.get("speech_analysis", {})
        if speech:
            conf = speech.get("confidence", {})
            if isinstance(conf, dict):
                breakdown = conf.get("breakdown", {})
                features["voice_confidence"] = breakdown.get("voice_confidence", 0.5)
                features["fluency"] = breakdown.get("fluency", 0.5)
                features["content_quality"] = breakdown.get("content_quality", 0.5)
            
            fillers = speech.get("fillers", {})
            if fillers:
                rate = fillers.get("filler_rate_per_minute", 5)
                features["filler_words"] = max(0, 1 - rate / 15)
        
        # From vision analysis
        vision = analysis.get("vision_analysis", {})
        if vision:
            gaze = vision.get("gaze_analysis", {})
            if gaze:
                features["eye_contact"] = gaze.get("eye_contact_percentage", 50) / 100
            
            posture = vision.get("posture_analysis", {})
            if posture:
                features["posture"] = posture.get("engagement_score", 0.5)
            
            expression = vision.get("expression_analysis", {})
            if expression:
                features["expressiveness"] = expression.get("emotional_congruence", 0.5)
        
        # From fusion
        fusion = analysis.get("fusion", {})
        if fusion:
            features["authenticity"] = fusion.get("authenticity_score", 0.5)
        
        return features
    
    def _generate_insights(
        self,
        lime: LIMEExplanation,
        shap: SHAPExplanation,
        cf: CounterfactualExplanation
    ) -> List[str]:
        """Generate actionable insights from all explanations"""
        insights = []
        
        # From LIME - what influenced the score
        if lime.top_positive_features:
            top_pos = lime.top_positive_features[0][0].replace("_", " ")
            insights.append(
                f"Your strong {top_pos} was a key factor in your performance"
            )
        
        if lime.top_negative_features:
            top_neg = lime.top_negative_features[0][0].replace("_", " ")
            insights.append(
                f"Focus on improving your {top_neg} for better scores"
            )
        
        # From counterfactuals - what to change
        if cf.counterfactuals:
            easy_changes = [
                c for c in cf.counterfactuals
                if c.difficulty == "easy"
            ]
            if easy_changes:
                feature = easy_changes[0].original_feature.replace("_", " ")
                insights.append(
                    f"Quick win: improving your {feature} is achievable and impactful"
                )
        
        # Effort assessment
        if cf.estimated_effort == "manageable":
            insights.append(
                "With focused practice, you can achieve significant improvement"
            )
        elif cf.estimated_effort == "significant":
            insights.append(
                "Improvement will require dedicated effort in multiple areas"
            )
        
        return insights[:4]  # Return top 4 insights
    
    def explain_specific_score(
        self,
        score_name: str,
        score_value: float,
        contributing_factors: Dict[str, float]
    ) -> Dict:
        """
        Explain a specific score.
        
        Args:
            score_name: Name of the score
            score_value: The score value
            contributing_factors: Factors that contributed
            
        Returns:
            Explanation as dictionary
        """
        # LIME
        lime_result = explain_score(score_name, score_value, contributing_factors)
        
        # SHAP
        shap_result = explain_with_shap(contributing_factors, score_value, score_name)
        
        # Counterfactuals
        cf_result = generate_counterfactuals(
            contributing_factors, score_value
        )
        
        return {
            "score_name": score_name,
            "score_value": score_value,
            "lime": lime_result,
            "shap": shap_result,
            "counterfactuals": cf_result
        }


def explain_analysis(
    analysis_result: Dict,
    target_score: Optional[float] = None
) -> Dict:
    """
    Convenience function for complete explainability.
    
    Args:
        analysis_result: Complete analysis results
        target_score: Optional target score
        
    Returns:
        Complete explanation as dictionary
    """
    pipeline = ExplainabilityPipeline()
    result = pipeline.explain(analysis_result, target_score)
    
    return {
        "lime": result.lime_explanation,
        "shap": result.shap_explanation,
        "counterfactuals": result.counterfactuals,
        "feature_importance": result.feature_importance,
        "actionable_insights": result.actionable_insights
    }
