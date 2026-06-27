"""
Interview Brain — The Heart of the System.

Responsibilities:
  1. Interview State Machine  (WAITING → QUESTION_ASKED → ANSWERING → EVALUATING → ...)
  2. Session Memory           (previous Q&A, topics covered, scores)
  3. Adaptive Question Gen    (uses TopicMemory + DifficultyPolicy + LLM)
  4. Answer Evaluation        (delegates to TechnicalEngine + CommunicationEngine)
  5. Confidence Aggregation   (delegates to ConfidenceEngine)
  6. Difficulty Adaptation    (DifficultyPolicy — embedded, not a separate file)

Data Flow:
    InterviewBrain
        ↓
    TopicMemory           → picks next unexplored topic
        ↓
    LLM (Gemini Flash)    → generates question with difficulty + topic hint
        ↓
    Candidate answers
        ↓
    TechnicalEngine       → technical_score, missing_points
    CommunicationEngine   → communication_score, structure_used
    ConfidenceEngine      ← speech_metrics + vision_metrics
        ↓
    DifficultyPolicy      → adjusts difficulty_modifier for next question
        ↓
    Session Memory updated
"""
import asyncio
from typing import Dict, Any, List, Optional
from app.services.llm_service import LLMService
from app.services.technical_engine import TechnicalEngine
from app.services.communication_engine import CommunicationEngine
from app.services.confidence_engine import ConfidenceEngine
from app.services.topic_memory import TopicMemory, TOPIC_PROGRESSIONS


# ---------------------------------------------------------------------------
# Difficulty Policy (embedded inside InterviewBrain — not a separate file)
# Maps difficulty_modifier (-2 to +2) to human labels and LLM instructions.
# ---------------------------------------------------------------------------
DIFFICULTY_LEVELS = {
    -2: {
        "label": "Easy",
        "instruction": "Ask a very basic, entry-level question. Focus on definitions and simple examples.",
    },
    -1: {
        "label": "Easy-Medium",
        "instruction": "Ask a slightly simpler question. Focus on fundamentals and common patterns.",
    },
     0: {
        "label": "Medium",
        "instruction": "Ask a standard intermediate-level question with some practical depth.",
    },
    +1: {
        "label": "Hard",
        "instruction": "Ask a challenging question. Include edge cases, trade-offs, and design decisions.",
    },
    +2: {
        "label": "Expert",
        "instruction": "Ask an expert-level question. Cover system design trade-offs, internal mechanics, or advanced optimizations.",
    },
}


class InterviewBrain:
    """
    Orchestrator for the entire interview session.

    One instance per active session. Holds all in-memory session state:
      - conversation history
      - topic memory
      - current difficulty modifier
      - question counter
    """

    def __init__(self):
        self.llm = LLMService(task="eval")          # Flash for all in-session tasks
        self.technical_engine = TechnicalEngine()
        self.communication_engine = CommunicationEngine()

    # ------------------------------------------------------------------
    # Memory & State Helpers
    # ------------------------------------------------------------------

    def _build_conversation_context(self, history: List[Dict[str, str]]) -> str:
        """Formats conversation history for LLM context."""
        if not history:
            return "This is the first question."
        lines = []
        for i, turn in enumerate(history[-5:], 1):  # Last 5 turns only
            lines.append(f"Q{i}: {turn.get('question', '')}")
            lines.append(f"A{i}: {turn.get('answer', '')[:300]}...")
        return "\n".join(lines)

    def _clamp_modifier(self, modifier: int) -> int:
        return max(-2, min(2, modifier))

    # ------------------------------------------------------------------
    # Difficulty Policy
    # ------------------------------------------------------------------

    def get_difficulty_label(self, modifier: int) -> str:
        """Returns human-readable difficulty label for the current modifier."""
        return DIFFICULTY_LEVELS.get(self._clamp_modifier(modifier), DIFFICULTY_LEVELS[0])["label"]

    def compute_difficulty_delta(
        self,
        technical_score: float,
        confidence_score: float,
        current_modifier: int,
    ) -> int:
        """
        Computes the recommended change to difficulty_modifier after an answer.

        Logic:
          - Both strong (tech ≥ 75 AND confidence ≥ 70) → increase difficulty (+1)
          - Both weak   (tech < 50 AND confidence < 50) → decrease difficulty (-1)
          - Mixed                                        → no change (0)

        The caller adds this delta to the session's difficulty_modifier.
        """
        strong = technical_score >= 75 and confidence_score >= 70
        weak   = technical_score < 50  and confidence_score < 50

        if strong:
            delta = +1
        elif weak:
            delta = -1
        else:
            delta = 0

        # Clamp result so we don't drift past ±2
        new_modifier = self._clamp_modifier(current_modifier + delta)
        return new_modifier - current_modifier  # Return only the delta

    # ------------------------------------------------------------------
    # Question Generation
    # ------------------------------------------------------------------

    async def generate_next_question(
        self,
        job_role: str,
        history: List[Dict[str, str]],
        difficulty_modifier: int = 0,
        topic_memory: Optional[TopicMemory] = None,
    ) -> Dict[str, Any]:
        """
        Generates the next interview question.

        Returns:
            question_text, topic, subtopic, difficulty (label), difficulty_modifier
        """
        modifier = self._clamp_modifier(difficulty_modifier)
        diff_config = DIFFICULTY_LEVELS[modifier]
        conversation_context = self._build_conversation_context(history)

        # Topic guidance from TopicMemory
        topic_instruction = ""
        if topic_memory:
            next_topic = topic_memory.get_next_suggested_topic(job_role)
            if next_topic:
                suggested = ", ".join(next_topic["subtopics"][:3])
                topic_instruction = (
                    f"Focus on the topic: **{next_topic['topic']}** "
                    f"(possible subtopics: {suggested})."
                )
            elif topic_memory.covered_topics:
                topic_instruction = "All mapped topics have been covered. Ask an advanced, novel question."

        system_prompt = (
            f"You are an expert interviewer for a {job_role} position. "
            f"{diff_config['instruction']}"
        )

        prompt = f"""
Job Role: {job_role}
Difficulty Level: {diff_config['label']}

Recent Conversation:
{conversation_context}

{topic_instruction}

Generate ONE natural interview question. Avoid repeating anything from the recent conversation.

Return ONLY a JSON object:
{{
    "question_text": "<the full question>",
    "topic": "<main topic category>",
    "subtopic": "<specific subtopic>",
    "difficulty": "<beginner|intermediate|advanced|expert>"
}}
"""
        result = await self.llm.generate_json(prompt, system_prompt)
        result["difficulty_modifier"] = modifier
        result["difficulty_label"] = diff_config["label"]
        return result

    async def generate_followup_question(
        self,
        job_role: str,
        previous_question: str,
        previous_answer: str,
        missing_points: List[str],
        difficulty_modifier: int = 0,
    ) -> str:
        """
        Generates a targeted follow-up probing the specific missing technical points.
        Returns plain question text.
        """
        modifier = self._clamp_modifier(difficulty_modifier)
        diff_config = DIFFICULTY_LEVELS[modifier]

        system_prompt = (
            f"You are a senior interviewer for a {job_role} position probing an incomplete answer. "
            f"{diff_config['instruction']}"
        )
        prompt = f"""
Original Question: {previous_question}
Candidate's Answer: {previous_answer}
Missing Concepts: {', '.join(missing_points)}

Generate a single natural follow-up question that directly probes the missing concepts.
Respond with ONLY the question text — no preamble, no numbering, no explanation.
"""
        response = await self.llm.generate_text(prompt, system_prompt, temperature=0.6)
        return response.strip().strip('"')

    # ------------------------------------------------------------------
    # Answer Evaluation (full pipeline)
    # ------------------------------------------------------------------

    async def evaluate_answer(
        self,
        question: str,
        candidate_answer: str,
        job_role: str,
        template_weights: Optional[Dict[str, int]] = None,
        speech_metrics: Optional[Dict[str, Any]] = None,
        vision_metrics: Optional[Dict[str, Any]] = None,
        current_difficulty_modifier: int = 0,
    ) -> Dict[str, Any]:
        """
        Full evaluation pipeline for one answer.

        Steps:
          1. TechnicalEngine   → technical_score, missing_points
          2. CommunicationEngine → communication_score, structure
          3. ConfidenceEngine  → fuses speech + vision → confidence_score
          4. DifficultyPolicy  → computes difficulty delta for next question
          5. Weighted overall_score

        Returns a complete evaluation dict ready to be stored in the DB.
        """
        weights = template_weights or {
            "technical": 60,
            "communication": 25,
            "speech": 10,
            "confidence": 5,
        }

        # Run technical and communication evaluation in parallel
        tech_result, comm_result = await asyncio.gather(
            self.technical_engine.evaluate(question, candidate_answer, job_role),
            self.communication_engine.evaluate(candidate_answer, job_role),
        )

        technical_score    = tech_result.get("technical_score", 0)
        communication_score = comm_result.get("communication_score", 0)

        # Confidence from multimodal signals
        speech  = speech_metrics or {}
        vision  = vision_metrics or {}

        confidence_result = ConfidenceEngine.calculate_confidence(
            speech_fluency_score   = speech.get("fluency_score", 50),
            eye_contact_percent    = vision.get("eye_contact_percent", 50),
            head_stability_score   = vision.get("head_stability_score", 50),
            facial_engagement_score= vision.get("avg_engagement", 50),
        )
        confidence_score = confidence_result["confidence_score"]
        fluency_score    = speech.get("fluency_score", 50)

        # Weighted overall score
        total_weight = sum(weights.values()) or 100
        overall_score = round(
            (
                technical_score     * weights.get("technical", 60)
                + communication_score * weights.get("communication", 25)
                + fluency_score       * weights.get("speech", 10)
                + confidence_score    * weights.get("confidence", 5)
            ) / total_weight,
            1,
        )

        # Difficulty Policy — compute delta for next question
        difficulty_delta = self.compute_difficulty_delta(
            technical_score=technical_score,
            confidence_score=confidence_score,
            current_modifier=current_difficulty_modifier,
        )
        new_difficulty_modifier = self._clamp_modifier(current_difficulty_modifier + difficulty_delta)

        return {
            # Scores
            "overall_score":        overall_score,
            "technical_score":      technical_score,
            "communication_score":  communication_score,
            "confidence_score":     confidence_score,
            "fluency_score":        fluency_score,
            # Technical detail
            "technical_feedback":        tech_result.get("technical_feedback", ""),
            "technical_strengths":       tech_result.get("strengths", []),
            "technical_weaknesses":      tech_result.get("weaknesses", []),
            "missing_technical_points":  tech_result.get("missing_technical_points", []),
            "is_technically_complete":   tech_result.get("is_technically_complete", True),
            # Communication detail
            "communication_feedback":    comm_result.get("communication_feedback", ""),
            "communication_strengths":   comm_result.get("strengths", []),
            "communication_weaknesses":  comm_result.get("weaknesses", []),
            "structure_used":            comm_result.get("structure_used", "Unstructured"),
            "vocabulary_level":          comm_result.get("vocabulary_level", "basic"),
            "improvement_tips":          comm_result.get("improvement_tips", []),
            # Confidence detail
            "confidence_band":           confidence_result["confidence_band"],
            "confidence_components":     confidence_result["components"],
            # Difficulty adaptation
            "difficulty_delta":          difficulty_delta,
            "new_difficulty_modifier":   new_difficulty_modifier,
            "new_difficulty_label":      self.get_difficulty_label(new_difficulty_modifier),
            # Weights used
            "weights_used": weights,
        }
