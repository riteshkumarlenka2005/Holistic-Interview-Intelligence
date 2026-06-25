"""
Confidence Scoring Module
Scores overall speaking confidence based on multiple prosodic and linguistic factors
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class ConfidenceBreakdown:
    """Breakdown of confidence score components"""
    voice_confidence: float  # Based on prosody (pitch, energy)
    fluency: float  # Based on filler rate and pauses
    content_quality: float  # Based on answer structure
    pace_consistency: float  # Based on speaking pace
    expressiveness: float  # Based on pitch/energy variation


@dataclass
class ConfidenceResult:
    """Complete confidence scoring result"""
    overall_score: float  # 0-1 scale
    breakdown: ConfidenceBreakdown
    assessment: str  # Excellent, Good, Needs Improvement, etc.
    recommendations: List[str]
    confidence_level: str  # high, medium, low
    percentile: float  # Estimated percentile compared to typical candidates


# Benchmark values from typical interview settings
BENCHMARK_VALUES = {
    "filler_rate_good": 3.0,  # fillers per minute
    "filler_rate_bad": 10.0,
    "wpm_low": 100,
    "wpm_high": 180,
    "wpm_optimal": 140,
    "pitch_cv_low": 0.05,  # coefficient of variation
    "pitch_cv_high": 0.30,
    "energy_cv_low": 0.1,
    "energy_cv_high": 0.5,
    "pause_ratio_good": 0.15,  # pause time / total time
    "pause_ratio_bad": 0.35
}


def calculate_voice_confidence(prosody: Dict) -> float:
    """
    Calculate voice confidence from prosody analysis.
    
    High confidence indicators:
    - Moderate pitch variation (not monotone, not erratic)
    - Consistent energy/volume
    - Appropriate speaking pace
    
    Args:
        prosody: Prosody analysis results
        
    Returns:
        Voice confidence score 0-1
    """
    scores = []
    
    # Pitch analysis
    pitch = prosody.get("pitch", {})
    pitch_variability = pitch.get("variability", "unknown")
    pitch_std = pitch.get("std", 0)
    pitch_mean = pitch.get("mean", 0)
    
    if pitch_mean > 0:
        pitch_cv = pitch_std / pitch_mean
        # Moderate variation is best (0.1-0.2 CV)
        if 0.1 <= pitch_cv <= 0.25:
            pitch_score = 0.9
        elif pitch_cv < 0.1:
            pitch_score = 0.5  # Monotone
        elif pitch_cv < 0.35:
            pitch_score = 0.7  # Slightly erratic
        else:
            pitch_score = 0.4  # Very erratic
    else:
        pitch_score = 0.5
    scores.append(pitch_score)
    
    # Energy/volume consistency
    energy = prosody.get("energy", {})
    energy_variation = energy.get("variation", "moderate")
    if energy_variation == "moderate":
        energy_score = 0.85
    elif energy_variation == "low":
        energy_score = 0.6  # Too flat
    else:
        energy_score = 0.5  # Too variable
    scores.append(energy_score)
    
    # Tone assessment
    tone = prosody.get("tone", {})
    tone_overall = tone.get("overall", "neutral")
    tone_confidence = tone.get("confidence", 0.5)
    
    tone_score = 0.3 + (tone_confidence * 0.7)
    scores.append(tone_score)
    
    return float(np.mean(scores))


def calculate_fluency_score(fillers: Dict, pace: Dict) -> float:
    """
    Calculate fluency score from filler and pace analysis.
    
    Args:
        fillers: Filler word analysis results
        pace: Speaking pace analysis
        
    Returns:
        Fluency score 0-1
    """
    scores = []
    
    # Filler rate scoring
    filler_rate = fillers.get("filler_rate_per_minute", 0)
    if filler_rate <= BENCHMARK_VALUES["filler_rate_good"]:
        filler_score = 0.95
    elif filler_rate <= 5:
        filler_score = 0.8
    elif filler_rate <= BENCHMARK_VALUES["filler_rate_bad"]:
        filler_score = 0.5
    else:
        filler_score = 0.3
    scores.append(filler_score * 1.5)  # Weight fillers more heavily
    
    # Pause ratio scoring
    pauses = pace.get("pauses", [])
    total_pause = sum(p.get("duration", 0) for p in pauses) if pauses else 0
    total_duration = pace.get("total_duration", 60)  # Assume 60s if not provided
    
    pause_ratio = total_pause / total_duration if total_duration > 0 else 0
    if pause_ratio <= BENCHMARK_VALUES["pause_ratio_good"]:
        pause_score = 0.9
    elif pause_ratio <= 0.25:
        pause_score = 0.7
    elif pause_ratio <= BENCHMARK_VALUES["pause_ratio_bad"]:
        pause_score = 0.5
    else:
        pause_score = 0.3
    scores.append(pause_score)
    
    # Count long hesitation pauses
    hesitation_count = sum(1 for p in pauses if p.get("type") == "hesitation") if pauses else 0
    hesitation_penalty = min(0.2, hesitation_count * 0.02)
    
    base_score = sum(scores) / (1 + 1.5)  # Normalize by weights
    return float(max(0, min(1, base_score - hesitation_penalty)))


def calculate_pace_consistency(pace: Dict) -> float:
    """
    Calculate pace consistency score.
    
    Args:
        pace: Speaking pace analysis
        
    Returns:
        Pace consistency score 0-1
    """
    wpm = pace.get("words_per_minute", 0)
    assessment = pace.get("assessment", "normal")
    
    # Optimal range scoring
    if BENCHMARK_VALUES["wpm_low"] <= wpm <= BENCHMARK_VALUES["wpm_high"]:
        # Score based on how close to optimal
        distance_from_optimal = abs(wpm - BENCHMARK_VALUES["wpm_optimal"])
        max_distance = max(
            BENCHMARK_VALUES["wpm_optimal"] - BENCHMARK_VALUES["wpm_low"],
            BENCHMARK_VALUES["wpm_high"] - BENCHMARK_VALUES["wpm_optimal"]
        )
        base_score = 0.7 + (1 - distance_from_optimal / max_distance) * 0.3
    elif wpm < BENCHMARK_VALUES["wpm_low"]:
        base_score = 0.4  # Too slow
    else:
        base_score = 0.5  # Too fast
    
    return float(base_score)


def calculate_content_quality(content: Dict) -> float:
    """
    Calculate content quality score.
    
    Args:
        content: Content analysis results (from LLM or NLP)
        
    Returns:
        Content quality score 0-1
    """
    if not content:
        return 0.6  # Default neutral score
    
    scores = []
    
    # Structure score (STAR method usage)
    structure_score = content.get("structure_score", 0.5)
    scores.append(structure_score)
    
    # Relevance score
    relevance = content.get("relevance_score", 0.5)
    scores.append(relevance)
    
    # Specificity score
    specificity = content.get("specificity_score", 0.5)
    scores.append(specificity)
    
    # Clarity score
    clarity = content.get("clarity_score", 0.5)
    scores.append(clarity)
    
    return float(np.mean(scores)) if scores else 0.6


def calculate_expressiveness(prosody: Dict) -> float:
    """
    Calculate expressiveness score.
    
    Args:
        prosody: Prosody analysis results
        
    Returns:
        Expressiveness score 0-1
    """
    tone = prosody.get("tone", {})
    expressiveness = tone.get("expressiveness", 0.5)
    monotone_score = tone.get("monotone_score", 0.5)
    
    # Higher expressiveness, lower monotone = better
    score = (expressiveness + (1 - monotone_score)) / 2
    return float(score)


def calculate_confidence_score(
    prosody: Dict,
    fillers: Dict,
    content_quality: Dict,
    visual_analysis: Optional[Dict] = None
) -> Dict:
    """
    Calculate overall confidence score with detailed breakdown.
    
    Args:
        prosody: Prosody analysis results
        fillers: Filler word analysis
        content_quality: Content quality metrics (from answer analysis)
        visual_analysis: Optional visual cues (from vision analysis)
        
    Returns:
        Confidence score dictionary with breakdown and recommendations
    """
    # Calculate component scores
    voice_confidence = calculate_voice_confidence(prosody)
    fluency = calculate_fluency_score(fillers, prosody.get("pace", {}))
    content_score = calculate_content_quality(content_quality)
    pace_consistency = calculate_pace_consistency(prosody.get("pace", {}))
    expressiveness = calculate_expressiveness(prosody)
    
    # Create breakdown
    breakdown = ConfidenceBreakdown(
        voice_confidence=voice_confidence,
        fluency=fluency,
        content_quality=content_score,
        pace_consistency=pace_consistency,
        expressiveness=expressiveness
    )
    
    # Calculate weighted overall score
    weights = {
        "voice_confidence": 0.20,
        "fluency": 0.25,
        "content_quality": 0.30,
        "pace_consistency": 0.10,
        "expressiveness": 0.15
    }
    
    # Optional visual boost
    if visual_analysis:
        visual_confidence = visual_analysis.get("confidence_score", 0)
        eye_contact = visual_analysis.get("eye_contact_percentage", 0) / 100
        posture_score = visual_analysis.get("posture_score", 0.5)
        
        visual_boost = (visual_confidence * 0.3 + eye_contact * 0.4 + posture_score * 0.3)
        # Visual contributes 20% of total
        weights = {k: v * 0.8 for k, v in weights.items()}
        overall = (
            voice_confidence * weights["voice_confidence"] +
            fluency * weights["fluency"] +
            content_score * weights["content_quality"] +
            pace_consistency * weights["pace_consistency"] +
            expressiveness * weights["expressiveness"] +
            visual_boost * 0.20
        )
    else:
        overall = (
            voice_confidence * weights["voice_confidence"] +
            fluency * weights["fluency"] +
            content_score * weights["content_quality"] +
            pace_consistency * weights["pace_consistency"] +
            expressiveness * weights["expressiveness"]
        )
    
    overall = float(max(0, min(1, overall)))
    
    # Determine assessment label
    assessment = get_assessment_label(overall)
    
    # Determine confidence level
    if overall >= 0.75:
        confidence_level = "high"
    elif overall >= 0.5:
        confidence_level = "medium"
    else:
        confidence_level = "low"
    
    # Estimate percentile (rough estimation)
    percentile = overall * 100  # Simplified linear mapping
    
    # Generate recommendations
    recommendations = generate_recommendations(
        voice_confidence, fluency, content_score,
        pace_consistency, expressiveness, prosody, fillers
    )
    
    result = ConfidenceResult(
        overall_score=overall,
        breakdown=breakdown,
        assessment=assessment,
        recommendations=recommendations,
        confidence_level=confidence_level,
        percentile=percentile
    )
    
    return {
        "overall_score": result.overall_score,
        "breakdown": {
            "voice_confidence": result.breakdown.voice_confidence,
            "fluency": result.breakdown.fluency,
            "content_quality": result.breakdown.content_quality,
            "pace_consistency": result.breakdown.pace_consistency,
            "expressiveness": result.breakdown.expressiveness
        },
        "assessment": result.assessment,
        "confidence_level": result.confidence_level,
        "percentile": result.percentile,
        "recommendations": result.recommendations
    }


def get_assessment_label(score: float) -> str:
    """Get human-readable assessment label from score"""
    if score >= 0.85:
        return "Excellent"
    elif score >= 0.70:
        return "Good"
    elif score >= 0.55:
        return "Satisfactory"
    elif score >= 0.40:
        return "Needs Improvement"
    else:
        return "Needs Significant Work"


def generate_recommendations(
    voice: float,
    fluency: float,
    content: float,
    pace: float,
    expressiveness: float,
    prosody: Dict,
    fillers: Dict
) -> List[str]:
    """Generate actionable recommendations based on scores"""
    recommendations = []
    
    # Voice confidence recommendations
    if voice < 0.6:
        pitch_var = prosody.get("pitch", {}).get("variability", "unknown")
        if pitch_var == "low":
            recommendations.append(
                "Vary your pitch to sound more engaging. Practice emphasizing "
                "key words and using rising intonation for questions."
            )
        elif pitch_var == "high":
            recommendations.append(
                "Your pitch variation is high, which may signal nervousness. "
                "Practice speaking with a more measured, steady tone."
            )
    
    # Fluency recommendations
    if fluency < 0.6:
        filler_rate = fillers.get("filler_rate_per_minute", 0)
        if filler_rate > 5:
            recommendations.append(
                f"Reduce filler words (currently {filler_rate:.1f}/min). "
                "Replace 'um' and 'uh' with brief silent pauses."
            )
        
        # Check for specific fillers
        most_common = fillers.get("most_common", [])
        if most_common:
            top_filler = most_common[0][0] if most_common[0] else None
            if top_filler and top_filler in ["like", "you know", "basically"]:
                recommendations.append(
                    f"You frequently use '{top_filler}'. Practice eliminating "
                    "these hedging words to sound more confident."
                )
    
    # Pace recommendations
    if pace < 0.6:
        wpm = prosody.get("pace", {}).get("words_per_minute", 0)
        if wpm < 100:
            recommendations.append(
                "Your speaking pace is slow. Practice speaking at 130-150 words "
                "per minute to maintain listener engagement."
            )
        elif wpm > 180:
            recommendations.append(
                "You're speaking very quickly. Slow down to ensure clarity and "
                "give yourself time to think. Aim for 130-150 words per minute."
            )
    
    # Expressiveness recommendations
    if expressiveness < 0.5:
        recommendations.append(
            "Add more vocal expressiveness to your delivery. Practice emphasizing "
            "important points and varying your energy level throughout your response."
        )
    
    # Content recommendations
    if content < 0.6:
        recommendations.append(
            "Structure your answers using the STAR method (Situation, Task, "
            "Action, Result) for behavioral questions."
        )
    
    # Positive feedback if doing well
    if not recommendations:
        if voice >= 0.8 and fluency >= 0.8:
            recommendations.append(
                "Excellent vocal delivery! Your confidence and fluency are strong. "
                "Continue practicing to maintain this level."
            )
        else:
            recommendations.append(
                "Good overall performance. Focus on consistency across all "
                "dimensions for even stronger delivery."
            )
    
    return recommendations[:5]  # Limit to top 5 recommendations
