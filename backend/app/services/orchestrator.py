"""
InterviewOrchestrator — Drives the full interview lifecycle.

Responsibilities:
  - Start a session → pick first question
  - Receive answer transcript → invoke InterviewBrain evaluation
  - Persist per-answer Response record with all scores
  - Update session difficulty_modifier based on Brain's recommendation
  - Determine FOLLOW_UP vs NEXT_QUESTION state transition
  - Generate adaptive or main question accordingly
"""
from typing import Dict, Any, Optional
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.interview import InterviewSession, InterviewState, InterviewTemplate
from app.models.questions import InterviewQuestion
from app.models.responses import Response
from app.services.interview_brain import InterviewBrain
from app.services.topic_memory import TopicMemory
from app.services.crud.interview import get_session


class InterviewOrchestrator:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.brain = InterviewBrain()

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _load_topic_memory(self, session: InterviewSession) -> TopicMemory:
        """Deserializes TopicMemory from the session's asked_topics JSON field."""
        return TopicMemory(asked_topics=session.asked_topics or [])
    # ------------------------------------------------------------------

    async def _get_template_weights(self, session: InterviewSession) -> Dict[str, int]:
        """
        Fetches dynamic scoring weights from the InterviewTemplate
        linked to the session, or falls back to sensible defaults.
        """
        template_id = getattr(session, "template_id", None)
        if template_id:
            result = await self.db.execute(
                select(InterviewTemplate).where(InterviewTemplate.id == template_id)
            )
            template = result.scalar_one_or_none()
            if template:
                return {
                    "technical": template.technical_weight,
                    "communication": template.communication_weight,
                    "speech": template.speech_weight,
                    "confidence": template.confidence_weight,
                }
        # Default: general-purpose technical interview
        return {"technical": 60, "communication": 25, "speech": 10, "confidence": 5}

    async def _save_question(
        self,
        session_id: str,
        question_text: str,
        order_index: int,
        was_follow_up: bool = False,
    ) -> InterviewQuestion:
        """Persists a new question and returns the saved ORM object."""
        iv_question = InterviewQuestion(
            session_id=session_id,
            question_text=question_text,
            asked_at=datetime.now(timezone.utc),
            order_index=order_index,
            was_follow_up=was_follow_up,
        )
        self.db.add(iv_question)
        await self.db.flush()
        await self.db.refresh(iv_question)
        return iv_question

    async def _count_questions(self, session_id: str) -> int:
        result = await self.db.execute(
            select(InterviewQuestion).where(InterviewQuestion.session_id == session_id)
        )
        return len(result.scalars().all())

    async def _save_response(
        self,
        session_id: str,
        question_id: str,
        transcript: str,
        evaluation: Dict[str, Any],
        speech_metrics: Optional[Dict[str, Any]] = None,
    ) -> Response:
        """Persists a per-answer Response record with all engine scores."""
        response = Response(
            session_id=session_id,
            question_id=question_id,
            transcript_text=transcript,
            word_count=evaluation.get("fluency_score"),  # proxy via speech_metrics
            technical_score=evaluation.get("technical_score"),
            communication_score=evaluation.get("communication_score"),
            speech_metrics=speech_metrics or {"fluency_score": evaluation.get("fluency_score")},
            feedback=(
                f"Technical: {evaluation.get('technical_feedback', '')} | "
                f"Communication: {evaluation.get('communication_feedback', '')}"
            ),
            detailed_feedback={
                "technical_strengths": evaluation.get("technical_strengths", []),
                "technical_weaknesses": evaluation.get("technical_weaknesses", []),
                "communication_strengths": evaluation.get("communication_strengths", []),
                "communication_weaknesses": evaluation.get("communication_weaknesses", []),
                "missing_technical_points": evaluation.get("missing_technical_points", []),
            }
        )
        self.db.add(response)
        await self.db.flush()
        return response

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    async def start_session(self, session_id: str) -> Dict[str, Any]:
        """
        Transitions session from WAITING -> QUESTION_ASKED.
        Generates and persists the first question using TopicMemory.
        """
        session = await get_session(self.db, session_id=session_id)
        if not session:
            raise ValueError(f"Session {session_id!r} not found")

        session.current_state = InterviewState.QUESTION_ASKED.value
        session.status = "in_progress"
        session.started_at = datetime.now(timezone.utc)

        job_role = session.target_job_role or "Software Engineer"
        topic_memory = self._load_topic_memory(session)

        q_result = await self.brain.generate_next_main_question(
            job_role=job_role,
            interview_context=[],
            difficulty_modifier=session.difficulty_modifier,
            topic_memory=topic_memory,
        )

        # Record the topic so it won't be repeated
        topic_memory.record(
            topic=q_result.get("topic", "General"),
            subtopic=q_result.get("subtopic"),
            difficulty=q_result.get("difficulty", "intermediate"),
            question_text=q_result.get("question_text", ""),
        )
        session.asked_topics = topic_memory.to_list()

        iv_question = await self._save_question(
            session_id, q_result.get("question_text", ""), order_index=1
        )
        await self.db.commit()

        return {
            "session_id": session.id,
            "state": session.current_state,
            "question": {
                "id": iv_question.id,
                "text": iv_question.question_text,
                "topic": q_result.get("topic"),
                "subtopic": q_result.get("subtopic"),
                "order_index": 1,
                "is_follow_up": False,
            },
        }

    async def process_answer(
        self,
        session_id: str,
        question_id: str,
        transcript: str,
        speech_metrics: Optional[Dict[str, Any]] = None,
        vision_metrics: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Core adaptive flow:

        1. Fetch session + fetch template weights
        2. Transition state → EVALUATING
        3. Run Brain.evaluate_answer (parallel TechnicalEngine + CommunicationEngine)
        4. Persist per-answer Response with all scores
        5. Apply difficulty_delta to session.difficulty_modifier (clamped -2..+2)
        6. Branch: FOLLOW_UP or NEXT_QUESTION
        7. Generate next question, persist, transition → QUESTION_ASKED
        8. Return full payload to WebSocket
        """
        session = await get_session(self.db, session_id=session_id)
        if not session:
            raise ValueError(f"Session {session_id!r} not found")

        # Fetch the question text
        q_result = await self.db.execute(
            select(InterviewQuestion).where(InterviewQuestion.id == question_id)
        )
        iv_question = q_result.scalar_one_or_none()
        if not iv_question:
            raise ValueError(f"Question {question_id!r} not found")

        question_text = iv_question.question_text
        job_role = session.target_job_role or "Software Engineer"
        topic_memory = self._load_topic_memory(session)

        # -- State: EVALUATING --
        session.current_state = InterviewState.EVALUATING.value
        await self.db.flush()

        # — Dynamic weights from template —
        weights = await self._get_template_weights(session)

        # — Run Brain (TechnicalEngine + CommunicationEngine in parallel) —
        evaluation = await self.brain.evaluate_answer(
            question=question_text,
            candidate_answer=transcript,
            job_role=job_role,
            template_weights=weights,
            speech_metrics=speech_metrics,
            vision_metrics=vision_metrics,
        )

        # — Persist per-answer Response —
        await self._save_response(
            session_id=session_id,
            question_id=question_id,
            transcript=transcript,
            evaluation=evaluation,
            speech_metrics=speech_metrics,
        )

        # — Apply difficulty delta (clamp -2 to +2) —
        delta = evaluation.get("difficulty_delta", 0)
        session.difficulty_modifier = max(-2, min(2, session.difficulty_modifier + delta))

        # — Count existing questions for order_index —
        q_count = await self._count_questions(session_id)
        next_order = q_count + 1

        # — Branch: follow-up or next main question —
        missing_points = evaluation.get("missing_technical_points", [])
        is_complete = evaluation.get("is_technically_complete", True)

        if not is_complete and missing_points:
            session.current_state = InterviewState.FOLLOW_UP.value
            next_q_text = await self.brain.generate_adaptive_question(
                job_role=job_role,
                previous_question=question_text,
                previous_answer=transcript,
                missing_points=missing_points,
                difficulty_modifier=session.difficulty_modifier,
                topic_memory=topic_memory,
            )
            was_follow_up = True
            next_q_meta = {"topic": topic_memory.covered_topics[-1] if topic_memory.covered_topics else "General",
                           "subtopic": None}
        else:
            session.current_state = InterviewState.NEXT_QUESTION.value
            q_result_next = await self.brain.generate_next_main_question(
                job_role=job_role,
                interview_context=[],
                difficulty_modifier=session.difficulty_modifier,
                topic_memory=topic_memory,
            )
            next_q_text = q_result_next.get("question_text", "")
            next_q_meta = q_result_next
            # Record this new topic into memory
            topic_memory.record(
                topic=q_result_next.get("topic", "General"),
                subtopic=q_result_next.get("subtopic"),
                difficulty=q_result_next.get("difficulty", "intermediate"),
                question_text=next_q_text,
            )
            session.asked_topics = topic_memory.to_list()
            was_follow_up = False

        # -- Persist next question --
        next_question = await self._save_question(session_id, next_q_text, next_order, was_follow_up)
        session.current_state = InterviewState.QUESTION_ASKED.value
        await self.db.commit()

        return {
            "evaluation": {
                "overall_score": evaluation["overall_score"],
                "technical_score": evaluation["technical_score"],
                "communication_score": evaluation["communication_score"],
                "confidence_score": evaluation["confidence_score"],
                "confidence_band": evaluation.get("confidence_band", "Moderate"),
                "fluency_score": evaluation["fluency_score"],
                "technical_feedback": evaluation["technical_feedback"],
                "communication_feedback": evaluation["communication_feedback"],
                "structure_used": evaluation["structure_used"],
                "missing_technical_points": missing_points,
                "weights_used": evaluation["weights_used"],
            },
            "difficulty_modifier": session.difficulty_modifier,
            "next_action": "follow_up" if was_follow_up else "next_question",
            "next_question": {
                "id": next_question.id,
                "text": next_question.question_text,
                "topic": next_q_meta.get("topic") if not was_follow_up else None,
                "subtopic": next_q_meta.get("subtopic") if not was_follow_up else None,
                "order_index": next_order,
                "is_follow_up": was_follow_up,
            },
            "covered_topics": topic_memory.covered_topics,
        }
