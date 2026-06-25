"""
InterviewBrain — Pure Orchestrator.

Does NOT evaluate answers directly.
Delegates to:
  - TechnicalEngine  → technical correctness
  - CommunicationEngine → tone, clarity, STAR structure
  - SpeechEngine → transcription + acoustic metrics (via SpeechEngine.compute_metrics)

Then aggregates results using dynamic weights from the InterviewTemplate.
Also adjusts question difficulty using the session's difficulty_modifier.
"""
from typing import Dict, Any, List, Optional
from app.services.llm_service import LLMService
from app.services.technical_engine import TechnicalEngine
from app.services.communication_engine import CommunicationEngine
from app.services.confidence_engine import ConfidenceEngine
from app.services.topic_memory import TopicMemory, TOPIC_PROGRESSIONS


# Difficulty instruction fragments injected into question generation prompts
DIFFICULTY_INSTRUCTIONS = {
    -2: "Ask a very basic, entry-level question. Avoid all complex topics.",
    -1: "Ask a slightly simpler question. Focus on fundamentals.",
     0: "Ask a standard, intermediate-level question.",
    +1: "Ask a moderately challenging question. Include edge cases.",
    +2: "Ask an expert-level question. Include system design trade-offs or deep internals.",
}


class InterviewBrain:
    def __init__(self):
        self.llm = LLMService()
        self.technical_engine = TechnicalEngine()
        self.communication_engine = CommunicationEngine()

    # ------------------------------------------------------------------
    # Question Generation
    # ------------------------------------------------------------------

    async def generate_next_main_question(
        self,
        job_role: str,
        interview_context: List[Dict[str, str]],
        difficulty_modifier: int = 0,
        topic_memory: Optional[TopicMemory] = None,
    ) -> Dict[str, Any]:
        """
        Generates the next main interview question.
        
        - Consults TopicMemory to avoid repetition.
        - Uses the role's progression map to pick the next unexplored topic.
        - Adjusts complexity based on difficulty_modifier.
        
        Returns:
            Dict with 'question_text', 'topic', 'subtopic', 'difficulty'
        """
        difficulty_modifier = max(-2, min(2, difficulty_modifier))
        difficulty_hint = DIFFICULTY_INSTRUCTIONS.get(difficulty_modifier, DIFFICULTY_INSTRUCTIONS[0])

        system_prompt = (
            f"You are an expert interviewer for a {job_role} role. "
            f"{difficulty_hint}"
        )

        # Build topic context for the LLM
        topic_context = ""
        next_topic_entry = None
        if topic_memory:
            topic_context = topic_memory.format_for_prompt()
            next_topic_entry = topic_memory.get_next_suggested_topic(job_role)

        topic_instruction = ""
        if next_topic_entry:
            suggested_subtopics = ", ".join(next_topic_entry["subtopics"][:3])
            topic_instruction = (
                f"Focus this question on the topic: **{next_topic_entry['topic']}** "
                f"(suggested subtopics: {suggested_subtopics})."
            )
        elif topic_memory and topic_memory.covered_topics:
            topic_instruction = "All mapped topics have been covered. Ask a novel, advanced question on a different unexplored angle."

        prompt = f"""
        Job Role: {job_role}
        
        {topic_context}
        
        {topic_instruction}
        
        Generate a single, natural interview question. 
        Also classify it with the following JSON schema:
        {{
            "question_text": "<the full question text>",
            "topic": "<the main topic category, e.g. 'React Basics'>",
            "subtopic": "<the specific subtopic, e.g. 'Virtual DOM'>",
            "difficulty": "<one of: beginner, intermediate, advanced, expert>"
        }}
        """

        result = await self.llm.generate_json(prompt, system_prompt)
        return result

    async def generate_adaptive_question(
        self,
        job_role: str,
        previous_question: str,
        previous_answer: str,
        missing_points: List[str],
        difficulty_modifier: int = 0,
        topic_memory: Optional[TopicMemory] = None,
    ) -> str:
        """
        Generates a targeted follow-up question to probe missing technical points.
        Topic memory is passed for context but follow-ups stay on the current topic.
        """
        difficulty_modifier = max(-2, min(2, difficulty_modifier))
        difficulty_hint = DIFFICULTY_INSTRUCTIONS.get(difficulty_modifier, DIFFICULTY_INSTRUCTIONS[0])

        system_prompt = (
            f"You are an expert interviewer for a {job_role} role probing incomplete answers. "
            f"{difficulty_hint}"
        )

        prompt = f"""
        Previous Question: {previous_question}
        Candidate's Answer: {previous_answer}
        Missing Concepts: {', '.join(missing_points)}

        Generate a single natural follow-up question that probes specifically on the missing concepts.
        Respond with only the question text --- no preamble, no numbering.
        """

        response = await self.llm.generate_text(prompt, system_prompt, temperature=0.7)
        return response.strip(' "')

    # ------------------------------------------------------------------
    # Orchestrated Evaluation (delegates to engines)
    # ------------------------------------------------------------------

    async def evaluate_answer(
        self,
        question: str,
        candidate_answer: str,
        job_role: str,
        template_weights: Optional[Dict[str, int]] = None,
        speech_metrics: Optional[Dict[str, Any]] = None,
        vision_metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Full evaluation pipeline.

        1. TechnicalEngine  -> technical_score
        2. CommunicationEngine -> communication_score
        3. ConfidenceEngine -> fuses speech and vision metrics -> confidence_score
        4. Applies dynamic weights from InterviewTemplate (or defaults)
        5. Computes weighted overall_score
        6. Determines difficulty adjustment from ConfidenceEngine
        7. Returns full evaluation dict
        """
        # --- Default weights (technical-heavy, general purpose) ---
        weights = template_weights or {
            "technical": 70,
            "communication": 20,
            "speech": 10,
            "confidence": 0,
        }

        # --- Run engines in parallel ---
        import asyncio
        tech_result, comm_result = await asyncio.gather(
            self.technical_engine.evaluate(question, candidate_answer, job_role),
            self.communication_engine.evaluate(candidate_answer, job_role),
        )

        technical_score = tech_result.get("technical_score", 0)
        communication_score = comm_result.get("communication_score", 0)
        
        # --- Confidence Aggregation ---
        speech = speech_metrics or {}
        vision = vision_metrics or {}
        fluency_score = speech.get("fluency_score", 50)
        
        confidence_result = ConfidenceEngine.calculate_confidence(
            speech_fluency_score=fluency_score,
            eye_contact_percent=vision.get("eye_contact_percent", 50),
            head_stability_score=vision.get("head_stability_score", 50),
            facial_engagement_score=vision.get("avg_engagement", 50)
        )
        
        confidence_score = confidence_result["confidence_score"]
        difficulty_delta = confidence_result["difficulty_modifier_delta"]

        # --- Weighted overall score ---
        total_weight = sum(weights.values()) or 100
        overall_score = round(
            (technical_score * weights["technical"]
             + communication_score * weights["communication"]
             + fluency_score * weights.get("speech", 0)
             + confidence_score * weights.get("confidence", 0))
            / total_weight,
            1,
        )

        is_technically_complete = tech_result.get("is_technically_complete", True)

        return {
            "overall_score": overall_score,
            "technical_score": technical_score,
            "communication_score": communication_score,
            "confidence_score": confidence_score,
            "confidence_band": confidence_result["confidence_band"],
            "fluency_score": fluency_score,
            "weights_used": weights,
            "technical_feedback": tech_result.get("technical_feedback", ""),
            "technical_strengths": tech_result.get("strengths", []),
            "technical_weaknesses": tech_result.get("weaknesses", []),
            "communication_feedback": comm_result.get("communication_feedback", ""),
            "communication_strengths": comm_result.get("strengths", []),
            "communication_weaknesses": comm_result.get("weaknesses", []),
            "structure_used": comm_result.get("structure_used", ""),
            "missing_technical_points": tech_result.get("missing_technical_points", []),
            "is_technically_complete": is_technically_complete,
            "difficulty_delta": difficulty_delta,
        }
