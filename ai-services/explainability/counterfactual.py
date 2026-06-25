"""
Counterfactual Explanations Module
Generates "what-if" explanations for interview performance
"""
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np


@dataclass
class Counterfactual:
    """A single counterfactual explanation"""
    original_feature: str
    original_value: float
    suggested_value: float
    change_description: str
    predicted_improvement: float
    difficulty: str  # easy, moderate, hard
    action_steps: List[str]


@dataclass
class CounterfactualExplanation:
    """Complete counterfactual explanation"""
    original_score: float
    target_score: float
    counterfactuals: List[Counterfactual]
    minimal_changes_needed: int
    improvement_path: str
    estimated_effort: str


class CounterfactualGenerator:
    """
    Generates counterfactual explanations.
    Shows what changes would improve interview performance.
    """
    
    # Feature change difficulty ratings
    DIFFICULTY_MAP = {
        "voice_confidence": "moderate",
        "fluency": "moderate",
        "eye_contact": "easy",
        "posture": "easy",
        "content_quality": "hard",
        "expressiveness": "moderate",
        "pace": "easy",
        "filler_words": "moderate"
    }
    
    # Feature change action templates
    ACTION_TEMPLATES = {
        "voice_confidence": [
            "Practice speaking with a strong, clear voice",
            "Record yourself and listen back for hesitation",
            "Use power poses before interviews to boost confidence"
        ],
        "fluency": [
            "Replace filler words with brief pauses",
            "Practice answers out loud multiple times",
            "Use transition phrases instead of 'um' or 'like'"
        ],
        "eye_contact": [
            "Position camera at eye level",
            "Practice looking directly at the camera lens",
            "Place a small sticker near the camera as a focal point"
        ],
        "posture": [
            "Sit up straight with shoulders back",
            "Position your chair at the right height",
            "Keep feet flat on the floor for stability"
        ],
        "content_quality": [
            "Prepare STAR-format stories for common questions",
            "Research the company and role thoroughly",
            "Practice articulating your key accomplishments"
        ],
        "expressiveness": [
            "Practice varying your tone and pitch",
            "Use hand gestures naturally when speaking",
            "Smile genuinely when appropriate"
        ],
        "pace": [
            "Practice with a metronome at 120-150 words per minute",
            "Pause briefly between key points",
            "Record yourself and check pacing"
        ],
        "filler_words": [
            "Pause instead of saying 'um' or 'uh'",
            "Practice with a friend who counts your fillers",
            "Use the 'power of the pause' technique"
        ]
    }
    
    def __init__(self, improvement_threshold: float = 0.1):
        """
        Initialize counterfactual generator.
        
        Args:
            improvement_threshold: Minimum improvement to consider
        """
        self.improvement_threshold = improvement_threshold
    
    def generate_counterfactuals(
        self,
        current_features: Dict[str, float],
        current_score: float,
        target_score: Optional[float] = None,
        max_changes: int = 3
    ) -> CounterfactualExplanation:
        """
        Generate counterfactual explanations.
        
        Args:
            current_features: Current feature values
            current_score: Current overall score
            target_score: Desired target score (default: current + 0.15)
            max_changes: Maximum number of changes to suggest
            
        Returns:
            CounterfactualExplanation with suggested changes
        """
        if target_score is None:
            target_score = min(1.0, current_score + 0.15)
        
        improvement_needed = target_score - current_score
        
        if improvement_needed <= 0:
            return CounterfactualExplanation(
                original_score=current_score,
                target_score=target_score,
                counterfactuals=[],
                minimal_changes_needed=0,
                improvement_path="You've already achieved the target score!",
                estimated_effort="none"
            )
        
        # Find features with most improvement potential
        potential_improvements = []
        
        for feature, value in current_features.items():
            if value >= 0.9:  # Already excellent
                continue
            
            # Calculate potential improvement
            max_improvement = 1.0 - value
            impact = max_improvement * self._get_feature_weight(feature)
            
            if impact >= self.improvement_threshold / 2:
                potential_improvements.append({
                    "feature": feature,
                    "current": value,
                    "potential": value + max_improvement * 0.5,  # Realistic improvement
                    "impact": impact,
                    "difficulty": self.DIFFICULTY_MAP.get(feature, "moderate")
                })
        
        # Sort by impact/difficulty ratio (prefer high impact, low difficulty)
        difficulty_weights = {"easy": 0.3, "moderate": 0.6, "hard": 1.0}
        potential_improvements.sort(
            key=lambda x: x["impact"] / difficulty_weights[x["difficulty"]],
            reverse=True
        )
        
        # Generate counterfactuals for top changes
        counterfactuals = []
        accumulated_improvement = 0
        
        for imp in potential_improvements[:max_changes]:
            if accumulated_improvement >= improvement_needed:
                break
            
            feature = imp["feature"]
            current_val = imp["current"]
            target_val = min(0.95, imp["potential"])  # Cap at 95%
            
            cf = Counterfactual(
                original_feature=feature,
                original_value=current_val,
                suggested_value=target_val,
                change_description=self._generate_change_description(
                    feature, current_val, target_val
                ),
                predicted_improvement=imp["impact"] * 0.5,
                difficulty=imp["difficulty"],
                action_steps=self.ACTION_TEMPLATES.get(feature, [
                    f"Work on improving your {feature.replace('_', ' ')}"
                ])
            )
            counterfactuals.append(cf)
            accumulated_improvement += cf.predicted_improvement
        
        # Determine effort level
        difficulties = [cf.difficulty for cf in counterfactuals]
        if not difficulties:
            effort = "none"
        elif "hard" in difficulties:
            effort = "significant"
        elif difficulties.count("moderate") > 1:
            effort = "moderate"
        else:
            effort = "manageable"
        
        # Generate improvement path description
        path = self._generate_improvement_path(counterfactuals, target_score)
        
        return CounterfactualExplanation(
            original_score=current_score,
            target_score=target_score,
            counterfactuals=counterfactuals,
            minimal_changes_needed=len(counterfactuals),
            improvement_path=path,
            estimated_effort=effort
        )
    
    def generate_what_if(
        self,
        current_features: Dict[str, float],
        current_score: float,
        feature_to_change: str,
        new_value: float
    ) -> Dict:
        """
        Generate a single "what-if" scenario.
        
        Args:
            current_features: Current feature values
            current_score: Current score
            feature_to_change: Feature to modify
            new_value: New value for the feature
            
        Returns:
            What-if analysis
        """
        if feature_to_change not in current_features:
            return {
                "error": f"Unknown feature: {feature_to_change}",
                "valid_features": list(current_features.keys())
            }
        
        old_value = current_features[feature_to_change]
        change_direction = "increase" if new_value > old_value else "decrease"
        
        # Calculate predicted new score
        weight = self._get_feature_weight(feature_to_change)
        score_delta = (new_value - old_value) * weight
        predicted_score = max(0, min(1, current_score + score_delta))
        
        return {
            "feature": feature_to_change,
            "original_value": old_value,
            "new_value": new_value,
            "change_direction": change_direction,
            "change_magnitude": abs(new_value - old_value),
            "original_score": current_score,
            "predicted_score": predicted_score,
            "score_improvement": predicted_score - current_score,
            "is_beneficial": predicted_score > current_score,
            "action_steps": self.ACTION_TEMPLATES.get(feature_to_change, [])
        }
    
    def find_minimum_changes(
        self,
        current_features: Dict[str, float],
        current_score: float,
        target_score: float
    ) -> List[Dict]:
        """
        Find minimum changes needed to reach target score.
        
        Args:
            current_features: Current feature values
            current_score: Current score
            target_score: Desired score
            
        Returns:
            Minimum set of changes
        """
        if current_score >= target_score:
            return []
        
        improvement_needed = target_score - current_score
        changes = []
        accumulated = 0
        
        # Sort features by improvement potential per unit difficulty
        features = []
        for f, v in current_features.items():
            if v < 0.9:
                weight = self._get_feature_weight(f)
                difficulty = {"easy": 1, "moderate": 2, "hard": 3}.get(
                    self.DIFFICULTY_MAP.get(f, "moderate"), 2
                )
                potential = (0.9 - v) * weight
                features.append((f, v, potential, difficulty))
        
        features.sort(key=lambda x: x[2] / x[3], reverse=True)
        
        for f, current, potential, diff in features:
            if accumulated >= improvement_needed:
                break
            
            contribution = min(potential, improvement_needed - accumulated)
            new_value = current + contribution / self._get_feature_weight(f)
            
            changes.append({
                "feature": f,
                "from": current,
                "to": min(0.95, new_value),
                "contribution": contribution,
                "difficulty": self.DIFFICULTY_MAP.get(f, "moderate")
            })
            accumulated += contribution
        
        return changes
    
    def _get_feature_weight(self, feature: str) -> float:
        """Get weight of a feature in overall score"""
        weights = {
            "voice_confidence": 0.15,
            "fluency": 0.12,
            "content_quality": 0.18,
            "expressiveness": 0.10,
            "pace": 0.08,
            "filler_words": 0.10,
            "eye_contact": 0.12,
            "posture": 0.08,
            "expression": 0.07
        }
        return weights.get(feature, 0.1)
    
    def _generate_change_description(
        self,
        feature: str,
        current: float,
        target: float
    ) -> str:
        """Generate human-readable change description"""
        feature_name = feature.replace("_", " ")
        current_pct = int(current * 100)
        target_pct = int(target * 100)
        
        if current < 0.4:
            level = "limited"
        elif current < 0.6:
            level = "moderate"
        else:
            level = "good"
        
        if target < 0.6:
            goal = "average"
        elif target < 0.8:
            goal = "good"
        else:
            goal = "excellent"
        
        return (
            f"Improve your {feature_name} from {level} ({current_pct}%) "
            f"to {goal} ({target_pct}%)"
        )
    
    def _generate_improvement_path(
        self,
        counterfactuals: List[Counterfactual],
        target: float
    ) -> str:
        """Generate description of improvement path"""
        if not counterfactuals:
            return f"No changes needed to reach {target:.0%}"
        
        features = [cf.original_feature.replace("_", " ") for cf in counterfactuals]
        
        if len(features) == 1:
            return f"Focus on improving your {features[0]} to reach {target:.0%}"
        elif len(features) == 2:
            return f"Improve your {features[0]} and {features[1]} to reach {target:.0%}"
        else:
            return f"Work on {features[0]}, {features[1]}, and {len(features)-2} other areas to reach {target:.0%}"


def generate_counterfactuals(
    features: Dict[str, float],
    score: float,
    target: Optional[float] = None
) -> Dict:
    """
    Convenience function for counterfactual generation.
    
    Args:
        features: Current feature values
        score: Current score
        target: Target score
        
    Returns:
        Counterfactual explanation as dictionary
    """
    generator = CounterfactualGenerator()
    result = generator.generate_counterfactuals(features, score, target)
    
    return {
        "original_score": result.original_score,
        "target_score": result.target_score,
        "changes_needed": result.minimal_changes_needed,
        "estimated_effort": result.estimated_effort,
        "improvement_path": result.improvement_path,
        "counterfactuals": [
            {
                "feature": cf.original_feature,
                "current": cf.original_value,
                "suggested": cf.suggested_value,
                "description": cf.change_description,
                "predicted_improvement": cf.predicted_improvement,
                "difficulty": cf.difficulty,
                "action_steps": cf.action_steps
            }
            for cf in result.counterfactuals
        ]
    }


def what_if_analysis(
    features: Dict[str, float],
    score: float,
    change: Tuple[str, float]
) -> Dict:
    """
    Simple what-if analysis.
    
    Args:
        features: Current features
        score: Current score
        change: (feature_name, new_value) tuple
        
    Returns:
        What-if result
    """
    generator = CounterfactualGenerator()
    return generator.generate_what_if(features, score, change[0], change[1])
