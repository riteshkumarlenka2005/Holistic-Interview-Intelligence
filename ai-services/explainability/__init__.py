"""
Explainability Module
AI transparency and explanation features for interview analysis
"""

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

from .pipeline import (
    ExplainabilityPipeline,
    ExplainabilityResult,
    explain_analysis
)

__all__ = [
    # LIME
    "LIMEExplainer",
    "LIMEExplanation",
    "FeatureContribution",
    "explain_score",
    
    # SHAP
    "SHAPExplainer",
    "SHAPExplanation",
    "explain_with_shap",
    "get_feature_importance",
    
    # Counterfactual
    "CounterfactualGenerator",
    "CounterfactualExplanation",
    "Counterfactual",
    "generate_counterfactuals",
    "what_if_analysis",
    
    # Pipeline
    "ExplainabilityPipeline",
    "ExplainabilityResult",
    "explain_analysis"
]
