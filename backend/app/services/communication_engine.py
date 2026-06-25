from typing import Dict, Any
from app.services.llm_service import LLMService

class CommunicationEngine:
    def __init__(self):
        self.llm = LLMService()

    async def evaluate(self, candidate_answer: str, job_role: str) -> Dict[str, Any]:
        """
        Grades clarity, structure (e.g., STAR method usage), and professional tone.
        Returns a score (0-100), and communication feedback.
        """
        system_prompt = (
            f"You are an expert communication coach evaluating a candidate for a {job_role} position. "
            "Focus purely on how the candidate communicates: clarity, conciseness, use of structured frameworks (like STAR), and tone. "
            "Do not evaluate the technical correctness of their answer."
        )

        prompt = f"""
        Candidate Answer Transcript:
        {candidate_answer}
        
        Evaluate the communication style based on:
        1. Clarity and coherence.
        2. Structure (did they jump around, or was it organized?).
        3. Professional tone and confidence inferred from the transcript.
        
        Format your response as a JSON object with this exact schema:
        {{
            "communication_score": <int between 0 and 100>,
            "communication_feedback": "<string: concise 2-sentence feedback on their communication style>",
            "strengths": ["<string: specific communication strength>", ...],
            "weaknesses": ["<string: specific communication flaw or gap>", ...],
            "confidence_score": <int between 0 and 100>,
            "structure_used": "<string: e.g., 'STAR', 'Rambling', 'Direct', 'Unstructured'>"
        }}
        """

        evaluation = await self.llm.generate_json(prompt, system_prompt)
        return evaluation
