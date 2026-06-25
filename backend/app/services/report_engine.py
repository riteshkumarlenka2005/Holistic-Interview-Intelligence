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
        self.llm = LLMService()

    async def generate_reports(self, session_id: str) -> bool:
        """
        Main entry point for generating the Candidate and Recruiter reports.
        """
        # Fetch Session
        result = await self.db.execute(select(InterviewSession).where(InterviewSession.id == session_id))
        session = result.scalar_one_or_none()
        if not session:
            return False

        # Fetch Responses
        resp_result = await self.db.execute(
            select(Response).where(Response.session_id == session_id).order_by(Response.created_at)
        )
        responses = resp_result.scalars().all()

        # Fetch Integrity Events
        evt_result = await self.db.execute(
            select(IntegrityEvent).where(IntegrityEvent.session_id == session_id)
        )
        integrity_events = evt_result.scalars().all()

        # 1. Calculate Aggregates & Radar Data
        radar_data = self._calculate_radar_data(responses, integrity_events)
        
        # Readiness Score calculation (Headline metric)
        readiness_score = int(
            radar_data.get("technical", 0) * 0.40 +
            radar_data.get("communication", 0) * 0.25 +
            radar_data.get("confidence", 0) * 0.15 +
            radar_data.get("integrity", 0) * 0.20
        )
        
        # 2. Extract Question Breakdown
        question_breakdown = []
        for r in responses:
            df = r.detailed_feedback or {}
            question_breakdown.append({
                "question_id": r.question_id,
                "technical_score": r.technical_score,
                "communication_score": r.communication_score,
                "strengths": df.get("technical_strengths", []) + df.get("communication_strengths", []),
                "weaknesses": df.get("technical_weaknesses", []) + df.get("communication_weaknesses", []),
                "missing_points": df.get("missing_technical_points", [])
            })

        # 3. Generate Timeline
        timeline = self.timeline_engine.generate_timeline(
            session_started_at=session.started_at,
            responses=responses,
            integrity_events=integrity_events,
            session_ended_at=session.ended_at or session.updated_at
        )

        # 4. Generate LLM Executive Summary
        executive_summary = await self._generate_executive_summary(
            job_role=session.target_job_role or "Software Engineer",
            radar_data=radar_data,
            readiness_score=readiness_score,
            question_breakdown=question_breakdown
        )
        
        # 5. Determine Hiring Recommendation (Recruiter Report)
        hiring_recommendation = "Not Recommended"
        if readiness_score >= 80:
            hiring_recommendation = "Recommended"
        elif readiness_score >= 60:
            hiring_recommendation = "Recommended with Training"

        # 6. Build Report Payloads
        candidate_data = {
            "readiness_score": readiness_score,
            "executive_summary": executive_summary,
            "radar_data": radar_data,
            "question_breakdown": question_breakdown,
            "timeline": timeline,
            "learning_roadmap": self._generate_learning_roadmap(question_breakdown)
        }

        recruiter_data = {
            "readiness_score": readiness_score,
            "executive_summary": executive_summary,
            "radar_data": radar_data,
            "integrity_score": radar_data.get("integrity", 100),
            "integrity_summary": self.integrity_engine.generate_summary(integrity_events),
            "timeline": timeline,
            "hiring_recommendation": hiring_recommendation
        }

        # 7. Persist Reports
        candidate_report = Report(
            session_id=session_id,
            user_id=session.user_id,
            report_type="candidate",
            status="completed",
            data=candidate_data
        )
        recruiter_report = Report(
            session_id=session_id,
            user_id=session.user_id,
            report_type="recruiter",
            status="completed",
            data=recruiter_data
        )
        
        self.db.add(candidate_report)
        self.db.add(recruiter_report)
        await self.db.commit()
        
        return True

    def _calculate_radar_data(self, responses: List[Response], integrity_events: List[IntegrityEvent]) -> Dict[str, int]:
        tech_scores = [r.technical_score for r in responses if r.technical_score]
        comm_scores = [r.communication_score for r in responses if r.communication_score]
        
        avg_tech = sum(tech_scores) / len(tech_scores) if tech_scores else 0
        avg_comm = sum(comm_scores) / len(comm_scores) if comm_scores else 0
        
        # Rough confidence proxy from comm score for now until we store confidence per response directly
        # Or we can pull from speech_metrics
        conf_scores = []
        for r in responses:
            if r.speech_metrics and "fluency_score" in r.speech_metrics:
                conf_scores.append(r.speech_metrics["fluency_score"])
        avg_conf = sum(conf_scores) / len(conf_scores) if conf_scores else avg_comm
        
        integrity = self.integrity_engine.calculate_score(integrity_events)
        
        return {
            "technical": int(avg_tech),
            "communication": int(avg_comm),
            "confidence": int(avg_conf),
            "integrity": integrity,
            "problem_solving": int((avg_tech + avg_comm) / 2),
            "professionalism": int((avg_conf + integrity) / 2)
        }

    async def _generate_executive_summary(self, job_role: str, radar_data: Dict[str, int], readiness_score: int, question_breakdown: List[Dict[str, Any]]) -> str:
        prompt = f"""
        Generate a concise, professional 1-paragraph Executive Interview Summary for a {job_role} candidate.
        
        Scores:
        Readiness Score: {readiness_score}/100
        Technical: {radar_data.get('technical')}/100
        Communication: {radar_data.get('communication')}/100
        Integrity: {radar_data.get('integrity')}/100
        
        Write it in a professional, objective tone. Highlight their overall performance, key strengths, and an area for improvement.
        Return ONLY the raw paragraph text.
        """
        system_prompt = "You are an expert technical recruiter."
        return await self.llm.generate_text(prompt, system_prompt)

    def _generate_learning_roadmap(self, question_breakdown: List[Dict[str, Any]]) -> List[str]:
        # Collect weaknesses
        weaknesses = []
        for q in question_breakdown:
            weaknesses.extend(q.get("weaknesses", []))
            weaknesses.extend(q.get("missing_points", []))
            
        # Deduplicate and limit to top 5
        unique_w = list(set(weaknesses))[:5]
        return [f"Focus on improving: {w}" for w in unique_w]
