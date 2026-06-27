"""
Communication Evaluation Engine — Complete Implementation.

Evaluates candidate answers on:
  - Clarity and coherence
  - Grammar and vocabulary
  - Structure (STAR / Direct / Rambling detection)
  - Professional tone
  - Confidence inferred from transcript

Uses Gemini 2.5 Flash via LLMService.
"""
from typing import Dict, Any
from app.services.llm_service import LLMService


class CommunicationEngine:
    def __init__(self):
        self.llm = LLMService(task="eval")  # Flash tier

    async def evaluate(self, candidate_answer: str, job_role: str) -> Dict[str, Any]:
        """
        Evaluates communication quality of a candidate's transcript.

        Input:
            candidate_answer: The transcribed text of the candidate's response.
            job_role: Used to calibrate expected communication standards.

        Returns:
            communication_score (0-100)
            communication_feedback (string)
            strengths (list)
            weaknesses (list)
            confidence_score (0-100): inferred from language patterns
            structure_used: "STAR" | "Direct" | "Rambling" | "Unstructured"
            grammar_issues: int count of detected grammar problems
            vocabulary_level: "basic" | "intermediate" | "professional"
            improvement_tips: list[str]
        """
        if not candidate_answer or len(candidate_answer.strip()) < 10:
            return self._empty_result()

        system_prompt = (
            f"You are an expert communication coach evaluating a candidate for a {job_role} position. "
            "Focus purely on HOW the candidate communicates — clarity, structure, tone, vocabulary, "
            "and professional language. Do NOT evaluate technical correctness."
        )

        prompt = f"""
Candidate Answer Transcript:
\"\"\"{candidate_answer}\"\"\"

Evaluate the communication style. Return ONLY a valid JSON object:
{{
    "communication_score": <int 0-100>,
    "communication_feedback": "<2-sentence professional feedback on communication>",
    "strengths": ["<specific communication strength>", ...],
    "weaknesses": ["<specific communication flaw>", ...],
    "confidence_score": <int 0-100, inferred from language assertiveness>,
    "structure_used": "<one of: STAR, Direct, Analytical, Storytelling, Rambling, Unstructured>",
    "vocabulary_level": "<one of: basic, intermediate, professional, technical>",
    "grammar_issues": <int, estimated number of grammar/clarity issues>,
    "improvement_tips": ["<short actionable tip>", ...]
}}
"""
        try:
            result = await self.llm.generate_json(prompt, system_prompt)
            return self._normalize(result)
        except Exception:
            return self._empty_result()

    def _normalize(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Ensures all expected keys exist with valid values."""
        return {
            "communication_score": int(result.get("communication_score", 0)),
            "communication_feedback": result.get("communication_feedback", ""),
            "strengths": result.get("strengths", []),
            "weaknesses": result.get("weaknesses", []),
            "confidence_score": int(result.get("confidence_score", 50)),
            "structure_used": result.get("structure_used", "Unstructured"),
            "vocabulary_level": result.get("vocabulary_level", "basic"),
            "grammar_issues": int(result.get("grammar_issues", 0)),
            "improvement_tips": result.get("improvement_tips", []),
        }

    @staticmethod
    def _empty_result() -> Dict[str, Any]:
        return {
            "communication_score": 0,
            "communication_feedback": "No response provided.",
            "strengths": [],
            "weaknesses": ["No response detected."],
            "confidence_score": 0,
            "structure_used": "Unstructured",
            "vocabulary_level": "basic",
            "grammar_issues": 0,
            "improvement_tips": ["Please provide a complete answer."],
        }
