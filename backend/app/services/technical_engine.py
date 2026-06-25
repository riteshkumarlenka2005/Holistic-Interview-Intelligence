from typing import Dict, Any, List
from app.services.llm_service import LLMService

class TechnicalEngine:
    def __init__(self):
        self.llm = LLMService()

    async def evaluate(self, question: str, candidate_answer: str, job_role: str) -> Dict[str, Any]:
        """
        Rigorously assesses the raw technical correctness of an answer.
        Returns a score (0-100), technical feedback, missing technical points, and a completion flag.
        """
        system_prompt = (
            f"You are an expert technical interviewer evaluating a candidate for a {job_role} position. "
            "Focus purely on technical correctness, accuracy, and depth. Do not evaluate communication skills here."
        )

        prompt = f"""
        Question: {question}
        Candidate Answer: {candidate_answer}
        
        Evaluate the answer strictly on technical merit.
        Format your response as a JSON object with this exact schema:
        {{
            "technical_score": <int between 0 and 100>,
            "technical_feedback": "<string: concise 2-sentence technical feedback>",
            "strengths": ["<string: specific technical strength demonstrated>", ...],
            "weaknesses": ["<string: specific technical gap or flaw>", ...],
            "missing_technical_points": ["<string: key technical concept missing>", ...],
            "is_technically_complete": <boolean: whether the answer technically covered the core requirements>
        }}
        """

        evaluation = await self.llm.generate_json(prompt, system_prompt)
        return evaluation
