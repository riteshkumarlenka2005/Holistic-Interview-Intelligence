from typing import Dict, Any, List

class InterviewContextBuilder:
    """
    Aggregates Vision, Speech, Session, and Candidate data into a single payload.
    """
    @staticmethod
    def build_context(
        candidate_data: Dict[str, Any],
        session_data: Dict[str, Any],
        vision_metrics: Dict[str, Any],
        speech_metrics: Dict[str, Any],
        interview_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        
        return {
            "schema_version": "1.0",
            "InterviewSession": {
                "candidate": candidate_data,
                "session": session_data,
                "history": interview_history,
                "current_answer": {
                    "vision": vision_metrics,
                    "speech": speech_metrics
                }
            }
        }

class EvidenceBuilder:
    """
    Converts raw numerical metrics from the InterviewContext into structured,
    traceable evidence points for Gemini to reason over.
    """
    @staticmethod
    def build_evidence(context: Dict[str, Any]) -> Dict[str, List[Dict[str, Any]]]:
        current = context.get("InterviewSession", {}).get("current_answer", {})
        vision = current.get("vision", {})
        speech = current.get("speech", {})
        speech_metrics = speech.get("metrics", {})
        
        behavioral_evidence = []
        communication_evidence = []
        
        # Vision / Behavioral Evidence
        if "eye_contact_percent" in vision:
            behavioral_evidence.append({
                "type": "EYE_CONTACT",
                "value": vision["eye_contact_percent"],
                "source": "VisionMetrics"
            })
        
        if "avg_engagement" in vision:
            behavioral_evidence.append({
                "type": "FACIAL_ENGAGEMENT",
                "value": vision["avg_engagement"],
                "source": "VisionMetrics"
            })
            
        if "head_stability_score" in vision:
            behavioral_evidence.append({
                "type": "HEAD_STABILITY",
                "value": vision["head_stability_score"],
                "source": "VisionMetrics"
            })

        # Speech / Communication Evidence
        if "wpm" in speech_metrics:
            communication_evidence.append({
                "type": "PACE_WPM",
                "value": speech_metrics["wpm"],
                "source": "SpeechMetrics"
            })
            
        if "speaking_ratio" in speech_metrics:
            communication_evidence.append({
                "type": "SPEAKING_RATIO",
                "value": speech_metrics["speaking_ratio"],
                "source": "SpeechMetrics"
            })
            
        if "filler_words" in speech_metrics:
            filler_count = sum(speech_metrics["filler_words"].values())
            communication_evidence.append({
                "type": "FILLER_WORDS_TOTAL",
                "value": filler_count,
                "source": "SpeechMetrics"
            })
            
        if "restart_count" in speech_metrics:
            communication_evidence.append({
                "type": "RESTARTS",
                "value": speech_metrics["restart_count"],
                "source": "SpeechMetrics"
            })
            
        if "pause_count" in speech_metrics:
            communication_evidence.append({
                "type": "LONG_PAUSES",
                "value": speech_metrics["pause_count"],
                "source": "SpeechMetrics"
            })
            
        return {
            "behavioral_evidence": behavioral_evidence,
            "communication_evidence": communication_evidence
        }
