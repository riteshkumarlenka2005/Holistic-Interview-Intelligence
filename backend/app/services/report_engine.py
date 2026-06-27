"""
Report Engine — Candidate and Recruiter Report Generation.

Generates two reports per completed interview session:

Candidate Report:
    - Readiness Score (headline metric)
    - Executive Summary (LLM-generated, Gemini 2.5 Pro)
    - Radar Chart data (6 dimensions)
    - Question Breakdown (per-question scores and feedback)
    - Timeline (chronological events)
    - Learning Roadmap (top improvement areas)
    - Strengths and Weaknesses summary

Recruiter Report:
    - All above, plus:
    - Hiring Recommendation ("Recommended" / "Recommended with Training" / "Not Recommended")
    - Integrity summary
    - Risk level

Uses Gemini 2.5 Pro for executive summary (final output only).
Everything else is aggregation math — no LLM needed.
"""
import json
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.interview import InterviewSession
from app.models.responses import Response
from app.models.reports import Report
from app.models.integrity import IntegrityEvent
from app.services.integrity_engine import IntegrityEngine
from app.services.timeline_engine import TimelineEngine
from app.services.llm_service import LLMService


class ReportEngine:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.integrity_engine = IntegrityEngine()
        self.timeline_engine = TimelineEngine()
        self.llm = LLMService(task="report")   # Gemini 2.5 Pro for final report

    # ------------------------------------------------------------------
    # Main Entry Point
    # ------------------------------------------------------------------

    async def generate_reports(self, session_id: str) -> bool:
        """
        Generates Candidate and Recruiter reports for a completed session.

        Data Flow:
            DB → session + responses + integrity events
            ↓
            Radar data aggregation (math)
            ↓
            Readiness Score calculation (weighted math)
            ↓
            Executive Summary (Gemini 2.5 Pro)
            ↓
            Hiring Recommendation (rule-based)
            ↓
            Persist to DB
        """
        # Fetch session
        result = await self.db.execute(
            select(InterviewSession).where(InterviewSession.id == session_id)
        )
        session = result.scalar_one_or_none()
        if not session:
            return False

        # Fetch responses
        resp_result = await self.db.execute(
            select(Response)
            .where(Response.session_id == session_id)
            .order_by(Response.created_at)
        )
        responses = resp_result.scalars().all()

        # Fetch integrity events
        evt_result = await self.db.execute(
            select(IntegrityEvent).where(IntegrityEvent.session_id == session_id)
        )
        integrity_events = evt_result.scalars().all()

        job_role = session.target_job_role or "Software Engineer"

        # 1. Radar data (6 dimensions)
        radar_data = self._calculate_radar_data(responses, integrity_events)

        # 2. Readiness Score (headline metric)
        readiness_score = int(
            radar_data.get("technical", 0)      * 0.40 +
            radar_data.get("communication", 0)  * 0.25 +
            radar_data.get("confidence", 0)     * 0.15 +
            radar_data.get("integrity", 100)    * 0.20
        )

        # 3. Question-by-question breakdown
        question_breakdown = self._build_question_breakdown(responses)

        # 4. Timeline (chronological event log)
        timeline = self.timeline_engine.generate_timeline(
            session_started_at = session.started_at,
            responses          = responses,
            integrity_events   = integrity_events,
            session_ended_at   = session.ended_at or session.updated_at,
        )

        # 5. Executive Summary — Gemini 2.5 Pro
        executive_summary = await self._generate_executive_summary(
            job_role=job_role,
            radar_data=radar_data,
            readiness_score=readiness_score,
            question_breakdown=question_breakdown,
        )

        # 6. Learning Roadmap (top improvement areas from weaknesses)
        learning_roadmap = self._generate_learning_roadmap(question_breakdown)

        # 7. Strengths and weaknesses summary
        all_strengths  = self._collect_all(question_breakdown, "strengths")
        all_weaknesses = self._collect_all(question_breakdown, "weaknesses")

        # 8. Hiring Recommendation (rule-based — no LLM needed)
        if readiness_score >= 80:
            hiring_recommendation = "Recommended"
        elif readiness_score >= 60:
            hiring_recommendation = "Recommended with Training"
        else:
            hiring_recommendation = "Not Recommended"

        # 9. Integrity summary
        integrity_summary = self.integrity_engine.generate_summary(integrity_events)

        # Build report payloads
        candidate_data = {
            "readiness_score":    readiness_score,
            "executive_summary":  executive_summary,
            "radar_data":         radar_data,
            "question_breakdown": question_breakdown,
            "timeline":           timeline,
            "learning_roadmap":   learning_roadmap,
            "strengths":          all_strengths[:5],
            "weaknesses":         all_weaknesses[:5],
        }

        recruiter_data = {
            "readiness_score":       readiness_score,
            "executive_summary":     executive_summary,
            "radar_data":            radar_data,
            "question_breakdown":    question_breakdown,
            "timeline":              timeline,
            "hiring_recommendation": hiring_recommendation,
            "integrity_score":       integrity_summary["integrity_score"],
            "integrity_summary":     integrity_summary,
            "strengths":             all_strengths[:5],
            "weaknesses":            all_weaknesses[:5],
        }

        # Persist both reports
        for report_type, data in [("candidate", candidate_data), ("recruiter", recruiter_data)]:
            report = Report(
                session_id  = session_id,
                user_id     = session.user_id,
                report_type = report_type,
                status      = "completed",
                data        = data,
            )
            self.db.add(report)

        await self.db.commit()
        return True

    # ------------------------------------------------------------------
    # Internal Helpers
    # ------------------------------------------------------------------

    def _calculate_radar_data(
        self,
        responses: List[Response],
        integrity_events: List[IntegrityEvent],
    ) -> Dict[str, int]:
        """
        Aggregates response scores into 6 radar dimensions.

        Dimensions:
            technical       → avg of all technical_score
            communication   → avg of all communication_score
            confidence      → avg of fluency_score from speech_metrics
            integrity       → calculated by IntegrityEngine
            problem_solving → (technical + communication) / 2
            professionalism → (confidence + integrity) / 2
        """
        tech_scores = [r.technical_score for r in responses if r.technical_score is not None]
        comm_scores = [r.communication_score for r in responses if r.communication_score is not None]

        avg_tech = int(sum(tech_scores) / len(tech_scores)) if tech_scores else 0
        avg_comm = int(sum(comm_scores) / len(comm_scores)) if comm_scores else 0

        # Confidence from stored speech metrics
        conf_scores = []
        for r in responses:
            if r.speech_metrics and "fluency_score" in r.speech_metrics:
                conf_scores.append(r.speech_metrics["fluency_score"])
        avg_conf = int(sum(conf_scores) / len(conf_scores)) if conf_scores else max(avg_comm, 50)

        integrity = self.integrity_engine.calculate_score(integrity_events)

        return {
            "technical":       avg_tech,
            "communication":   avg_comm,
            "confidence":      avg_conf,
            "integrity":       integrity,
            "problem_solving": int((avg_tech + avg_comm) / 2),
            "professionalism": int((avg_conf + integrity) / 2),
        }

    def _build_question_breakdown(self, responses: List[Response]) -> List[Dict[str, Any]]:
        """Builds per-question breakdown from stored response data."""
        breakdown = []
        for r in responses:
            df = r.detailed_feedback or {}
            breakdown.append({
                "question_id":       str(r.question_id) if r.question_id else None,
                "technical_score":   r.technical_score,
                "communication_score": r.communication_score,
                "strengths":         df.get("technical_strengths", []) + df.get("communication_strengths", []),
                "weaknesses":        df.get("technical_weaknesses", []) + df.get("communication_weaknesses", []),
                "missing_points":    df.get("missing_technical_points", []),
                "structure_used":    df.get("structure_used", ""),
                "improvement_tips":  df.get("improvement_tips", []),
            })
        return breakdown

    def _collect_all(self, question_breakdown: List[Dict], key: str) -> List[str]:
        """Collects and deduplicates a field across all question breakdowns."""
        seen = set()
        result = []
        for q in question_breakdown:
            for item in q.get(key, []):
                if item and item not in seen:
                    seen.add(item)
                    result.append(item)
        return result

    def _generate_learning_roadmap(self, question_breakdown: List[Dict[str, Any]]) -> List[str]:
        """
        Extracts top improvement areas from weaknesses and missing points.
        Returns max 5 roadmap items.
        """
        items = set()
        for q in question_breakdown:
            items.update(q.get("weaknesses", []))
            items.update(q.get("missing_points", []))
        return [f"Focus on: {item}" for item in list(items)[:5]]

    async def _generate_executive_summary(
        self,
        job_role: str,
        radar_data: Dict[str, int],
        readiness_score: int,
        question_breakdown: List[Dict[str, Any]],
    ) -> str:
        """
        Generates a 2-paragraph executive summary using Gemini 2.5 Pro.

        Paragraph 1: Overall performance and key highlights.
        Paragraph 2: Specific strengths and the most important improvement area.
        """
        top_strengths = []
        top_weaknesses = []
        for q in question_breakdown:
            top_strengths.extend(q.get("strengths", []))
            top_weaknesses.extend(q.get("weaknesses", []))

        prompt = f"""
Generate a concise, professional 2-paragraph Executive Interview Summary.

Candidate Role: {job_role}
Readiness Score: {readiness_score}/100
Technical Score: {radar_data.get('technical')}/100
Communication Score: {radar_data.get('communication')}/100
Confidence Score: {radar_data.get('confidence')}/100
Integrity Score: {radar_data.get('integrity')}/100

Top Strengths: {', '.join(list(set(top_strengths))[:3])}
Top Weaknesses: {', '.join(list(set(top_weaknesses))[:3])}

Guidelines:
- Paragraph 1: Overall performance summary (2-3 sentences, professional tone)
- Paragraph 2: Key strengths demonstrated and the single most important area to improve (2-3 sentences)
- Use objective, neutral language suitable for a recruiter
- Do NOT use the word "impressive" or overly praise the candidate
- Return ONLY the two paragraphs as plain text
"""
        system_prompt = "You are a senior technical recruiter writing objective candidate assessments."
        return await self.llm.generate_text(prompt, system_prompt, temperature=0.4)
