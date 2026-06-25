"""
Multimodal Reasoning Pipeline
Complete pipeline for multimodal interview analysis
"""
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, asdict

from .fusion import (
    MultimodalFusion,
    FusionResult,
    FusionWeights,
    fuse_modalities,
    detect_incongruence
)
from .timeline_builder import (
    TimelineBuilder,
    build_timeline,
    build_multimodal_transcript
)
from .llm_reasoner import (
    LLMReasoner,
    LLMConfig,
    FeedbackResult,
    analyze_with_llm,
    generate_feedback
)


@dataclass
class ReasoningResult:
    """Complete multimodal reasoning result"""
    fusion: Dict
    timeline: Dict
    transcript: Dict
    llm_feedback: Optional[Dict]
    overall_assessment: Dict


class MultimodalReasoningPipeline:
    """
    Complete multimodal reasoning pipeline.
    Combines fusion, timeline building, and LLM-based analysis.
    """
    
    def __init__(
        self,
        fusion_weights: Optional[FusionWeights] = None,
        llm_config: Optional[LLMConfig] = None,
        enable_llm: bool = True
    ):
        """
        Initialize reasoning pipeline.
        
        Args:
            fusion_weights: Custom weights for modality fusion
            llm_config: LLM configuration
            enable_llm: Whether to enable LLM-based analysis
        """
        self.fusion = MultimodalFusion(fusion_weights)
        self.timeline_builder = TimelineBuilder()
        self.llm_reasoner = LLMReasoner(llm_config) if enable_llm else None
        self.enable_llm = enable_llm
    
    def analyze(
        self,
        speech_analysis: Dict,
        vision_analysis: Dict,
        question: Optional[str] = None,
        job_role: Optional[str] = None,
        include_llm_feedback: bool = True
    ) -> ReasoningResult:
        """
        Run complete multimodal reasoning.
        
        Args:
            speech_analysis: Results from speech analysis pipeline
            vision_analysis: Results from vision analysis pipeline
            question: Optional interview question for context
            job_role: Optional target job role
            include_llm_feedback: Whether to generate LLM feedback
            
        Returns:
            Complete ReasoningResult
        """
        # Step 1: Multimodal Fusion
        fusion_result = self.fusion.fuse(speech_analysis, vision_analysis)
        
        # Step 2: Build Timeline
        self.timeline_builder.reset()
        self.timeline_builder.add_speech_events(
            speech_analysis.get("transcription", {}),
            speech_analysis.get("prosody", {}),
            speech_analysis.get("fillers", {})
        )
        self.timeline_builder.add_vision_events(
            vision_analysis.get("gaze_analysis", {}),
            vision_analysis.get("posture_analysis", {}),
            vision_analysis.get("expression_analysis", {})
        )
        timeline = self.timeline_builder.to_dict()
        
        # Step 3: Build Multimodal Transcript
        transcript = self.timeline_builder.build_multimodal_transcript(
            speech_analysis.get("transcription", {}),
            vision_analysis.get("timeline", []),
            speech_analysis.get("timeline", [])
        )
        
        transcript_dict = {
            "segments": [
                {
                    "start": s.start_time,
                    "end": s.end_time,
                    "text": s.text,
                    "annotations": s.annotations
                }
                for s in transcript.segments
            ],
            "formatted_text": transcript.formatted_text,
            "summary": transcript.summary
        }
        
        # Step 4: LLM Feedback (if enabled)
        llm_feedback = None
        if include_llm_feedback and self.enable_llm and self.llm_reasoner:
            try:
                fusion_dict = {
                    "communication_score": fusion_result.communication_score,
                    "presence_score": fusion_result.presence_score,
                    "engagement_score": fusion_result.engagement_score,
                    "authenticity_score": fusion_result.authenticity_score,
                    "congruence_score": fusion_result.congruence.congruence_score
                }
                
                feedback_result = self.llm_reasoner.analyze_interview_performance(
                    speech_analysis, vision_analysis, fusion_dict,
                    question, job_role
                )
                
                llm_feedback = {
                    "overall_assessment": feedback_result.overall_assessment,
                    "strengths": feedback_result.strengths,
                    "areas_for_improvement": feedback_result.areas_for_improvement,
                    "specific_feedback": feedback_result.specific_feedback,
                    "actionable_tips": feedback_result.actionable_tips,
                    "follow_up_questions": feedback_result.follow_up_questions
                }
            except Exception as e:
                llm_feedback = {"error": str(e), "available": False}
        
        # Step 5: Generate Overall Assessment
        overall = self._generate_overall_assessment(
            fusion_result, timeline, speech_analysis, vision_analysis
        )
        
        # Convert fusion result to dict
        fusion_dict = {
            "combined_confidence": fusion_result.combined_confidence,
            "communication_score": fusion_result.communication_score,
            "presence_score": fusion_result.presence_score,
            "engagement_score": fusion_result.engagement_score,
            "authenticity_score": fusion_result.authenticity_score,
            "congruence": {
                "is_congruent": fusion_result.congruence.is_congruent,
                "score": fusion_result.congruence.congruence_score,
                "incongruent_areas": fusion_result.congruence.incongruent_areas,
                "interpretation": fusion_result.congruence.interpretation
            },
            "modality_contributions": fusion_result.modality_contributions,
            "assessment": fusion_result.integrated_assessment,
            "key_insights": fusion_result.key_insights
        }
        
        return ReasoningResult(
            fusion=fusion_dict,
            timeline=timeline,
            transcript=transcript_dict,
            llm_feedback=llm_feedback,
            overall_assessment=overall
        )
    
    def _generate_overall_assessment(
        self,
        fusion: FusionResult,
        timeline: Dict,
        speech: Dict,
        vision: Dict
    ) -> Dict:
        """Generate overall assessment summary"""
        # Calculate overall score
        scores = [
            fusion.combined_confidence,
            fusion.communication_score,
            fusion.presence_score,
            fusion.engagement_score
        ]
        overall_score = sum(scores) / len(scores)
        
        # Determine grade
        if overall_score >= 0.80:
            grade = "A"
            label = "Excellent"
        elif overall_score >= 0.70:
            grade = "B"
            label = "Good"
        elif overall_score >= 0.60:
            grade = "C"
            label = "Satisfactory"
        elif overall_score >= 0.50:
            grade = "D"
            label = "Needs Work"
        else:
            grade = "F"
            label = "Needs Significant Improvement"
        
        # Compile strengths and weaknesses
        strengths = []
        weaknesses = []
        
        # From speech
        confidence = speech.get("confidence", {})
        if confidence.get("overall_score", 0) >= 0.7:
            strengths.append("Strong vocal confidence")
        elif confidence.get("overall_score", 0) < 0.5:
            weaknesses.append("Vocal confidence needs improvement")
        
        # From vision
        gaze = vision.get("gaze_analysis", {})
        if gaze.get("eye_contact_percentage", 0) >= 60:
            strengths.append("Good eye contact")
        elif gaze.get("eye_contact_percentage", 0) < 40:
            weaknesses.append("Eye contact needs improvement")
        
        posture = vision.get("posture_analysis", {})
        if posture.get("dominant_posture") == "upright":
            strengths.append("Professional posture")
        elif posture.get("dominant_posture") in ["slouching"]:
            weaknesses.append("Posture needs attention")
        
        # From fusion
        if fusion.congruence.is_congruent:
            strengths.append("Authentic, congruent communication")
        else:
            weaknesses.append("Verbal and non-verbal cues are misaligned")
        
        # Event counts from timeline
        events = timeline.get("events", [])
        warning_count = sum(1 for e in events if e.get("severity") == "warning")
        
        return {
            "overall_score": round(overall_score * 100),
            "grade": grade,
            "label": label,
            "communication_score": round(fusion.communication_score * 100),
            "presence_score": round(fusion.presence_score * 100),
            "engagement_score": round(fusion.engagement_score * 100),
            "authenticity_score": round(fusion.authenticity_score * 100),
            "strengths": strengths[:4],
            "areas_for_improvement": weaknesses[:4],
            "notable_events": warning_count,
            "key_insights": fusion.key_insights[:3]
        }


def analyze_interview(
    speech_analysis: Dict,
    vision_analysis: Dict,
    question: Optional[str] = None,
    job_role: Optional[str] = None,
    enable_llm: bool = True
) -> Dict:
    """
    Complete interview analysis convenience function.
    
    Args:
        speech_analysis: Speech analysis results
        vision_analysis: Vision analysis results
        question: Optional interview question
        job_role: Optional target role
        enable_llm: Whether to enable LLM feedback
        
    Returns:
        Complete analysis as dictionary
    """
    pipeline = MultimodalReasoningPipeline(enable_llm=enable_llm)
    result = pipeline.analyze(
        speech_analysis, vision_analysis,
        question, job_role
    )
    
    return {
        "fusion": result.fusion,
        "timeline": result.timeline,
        "transcript": result.transcript,
        "llm_feedback": result.llm_feedback,
        "overall_assessment": result.overall_assessment
    }
