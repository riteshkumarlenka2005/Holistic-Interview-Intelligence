"""
Interview Brain — The Heart of the System (Phase 5)

Responsibilities:
  1. Integrates with LLMGateway for all Gemini reasoning.
  2. Uses InterviewContextBuilder & EvidenceBuilder to pass structured context to Gemini.
  3. Returns STRICT Pydantic models for Evaluation and Decision.
"""
import asyncio
from typing import Dict, Any, List, Optional

from app.services.llm_service import LLMGateway
from app.services.context_builder import InterviewContextBuilder, EvidenceBuilder
from app.models.evaluations import InterviewEvaluation, InterviewDecision
from app.services.topic_memory import TopicMemory
import json

class InterviewBrain:
    def __init__(self):
        # We strictly route through the LLM Gateway
        self.gateway = LLMGateway()

    def _build_history_context(self, history: List[Dict[str, Any]]) -> str:
        """Formats conversation history for LLM context."""
        if not history:
            return "This is the first question."
        return json.dumps(history, indent=2)

    async def evaluate_answer(
        self,
        question: str,
        candidate_answer: str,
        job_role: str,
        template_weights: Optional[Dict[str, int]] = None,
        speech_metrics: Optional[Dict[str, Any]] = None,
        vision_metrics: Optional[Dict[str, Any]] = None,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """
        Phase 5 Evaluation Pipeline.
        1. Build Unified Context
        2. Build Evidence
        3. Call Gemini for Evaluation (Structured Output)
        """
        history = history or []
        
        # 1. Build the Unified Interview Context
        context = InterviewContextBuilder.build_context(
            candidate_data={"role": job_role},
            session_data={},
            vision_metrics=vision_metrics or {},
            speech_metrics=speech_metrics or {},
            interview_history=history
        )
        
        # 2. Extract Evidence for the LLM
        evidence = EvidenceBuilder.build_evidence(context)
        
        system_prompt = (
            f"You are an expert technical interviewer evaluating a {job_role} candidate. "
            f"You will receive the candidate's transcript and structured behavioral/communication evidence. "
            f"Evaluate the candidate strictly based on the evidence provided."
        )
        
        prompt = f"""
Question Asked: {question}
Candidate Transcript: {candidate_answer}

Communication Evidence:
{json.dumps(evidence.get('communication_evidence', []), indent=2)}

Behavioral Evidence:
{json.dumps(evidence.get('behavioral_evidence', []), indent=2)}

Interview History (for context on progression):
{self._build_history_context(history)}

Generate a strictly structured evaluation matching the requested schema.
"""
        
        # 3. Call LLM Gateway for Evaluation
        evaluation: InterviewEvaluation = await self.gateway.generate_structured(
            prompt=prompt,
            response_model=InterviewEvaluation,
            system_prompt=system_prompt
        )
        
        # Return as dict for legacy DB compatibility during transition
        return evaluation.model_dump()


    async def generate_next_question(
        self,
        job_role: str,
        history: List[Dict[str, Any]],
        difficulty_modifier: int = 0,
        topic_memory: Optional[TopicMemory] = None,
        last_evaluation: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generates the next interview question or follow-up decision.
        """
        conversation_context = self._build_history_context(history)

        topic_instruction = ""
        if topic_memory:
            next_topic = topic_memory.get_next_suggested_topic(job_role)
            if next_topic:
                suggested = ", ".join(next_topic["subtopics"][:3])
                topic_instruction = f"Focus on the topic: **{next_topic['topic']}** (possible subtopics: {suggested})."

        system_prompt = (
            f"You are an expert interviewer for a {job_role} position. "
            f"Based on the conversation history and the most recent evaluation, decide the next best action. "
            f"You must decide whether to FOLLOW_UP on a weak point or ask the NEXT_QUESTION."
        )

        prompt = f"""
Job Role: {job_role}

Recent Conversation History:
{conversation_context}

Last Evaluation:
{json.dumps(last_evaluation, indent=2) if last_evaluation else "None"}

{topic_instruction}

Generate the decision.
"""
        
        decision: InterviewDecision = await self.gateway.generate_structured(
            prompt=prompt,
            response_model=InterviewDecision,
            system_prompt=system_prompt
        )
        
        return decision.model_dump()
