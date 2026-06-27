"""
Analytics Service — Dashboard Aggregation.

Pure aggregation over stored Report records — no LLM, no AI.

Provides:
    - Interview history (list with scores)
    - Performance trend (score over time)
    - Skill heatmap (per-topic average scores)
    - Readiness trend (readiness_score over time)
    - Interview comparison (side-by-side latest two)
"""
from typing import Dict, Any, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import func

from app.models.reports import Report
from app.models.interview import InterviewSession


class AnalyticsService:
    def __init__(self, db: AsyncSession):
        self.db = db

    # ------------------------------------------------------------------
    # Interview History
    # ------------------------------------------------------------------

    async def get_interview_history(
        self,
        user_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        """
        Returns a list of completed interviews with summary scores.
        """
        result = await self.db.execute(
            select(Report, InterviewSession)
            .join(InterviewSession, Report.session_id == InterviewSession.id)
            .where(
                Report.user_id    == user_id,
                Report.report_type == "candidate",
                Report.status      == "completed",
            )
            .order_by(Report.created_at.desc())
            .limit(limit)
        )
        rows = result.all()

        history = []
        for report, session in rows:
            data = report.data or {}
            history.append({
                "session_id":      str(session.id),
                "session_title":   session.title or f"{session.target_job_role} Interview",
                "job_role":        session.target_job_role,
                "completed_at":    session.ended_at.isoformat() if session.ended_at else None,
                "readiness_score": data.get("readiness_score", 0),
                "radar_data":      data.get("radar_data", {}),
            })
        return history

    # ------------------------------------------------------------------
    # Performance Trend
    # ------------------------------------------------------------------

    async def get_performance_trend(
        self,
        user_id: str,
        limit: int = 10,
    ) -> List[Dict[str, Any]]:
        """
        Returns readiness_score over time (oldest to newest).
        Used to draw the performance trend chart on the dashboard.
        """
        result = await self.db.execute(
            select(Report, InterviewSession)
            .join(InterviewSession, Report.session_id == InterviewSession.id)
            .where(
                Report.user_id     == user_id,
                Report.report_type == "candidate",
                Report.status      == "completed",
            )
            .order_by(Report.created_at.asc())
            .limit(limit)
        )
        rows = result.all()

        trend = []
        for report, session in rows:
            data = report.data or {}
            trend.append({
                "date":            session.ended_at.isoformat() if session.ended_at else None,
                "readiness_score": data.get("readiness_score", 0),
                "technical":       data.get("radar_data", {}).get("technical", 0),
                "communication":   data.get("radar_data", {}).get("communication", 0),
                "confidence":      data.get("radar_data", {}).get("confidence", 0),
            })
        return trend

    # ------------------------------------------------------------------
    # Skill Heatmap
    # ------------------------------------------------------------------

    async def get_skill_heatmap(self, user_id: str) -> List[Dict[str, Any]]:
        """
        Aggregates topic-level average scores across all interviews.

        Returns a list of topics with their average technical score,
        suitable for rendering a heatmap / radar chart.
        """
        result = await self.db.execute(
            select(Report)
            .where(
                Report.user_id     == user_id,
                Report.report_type == "candidate",
                Report.status      == "completed",
            )
        )
        reports = result.scalars().all()

        # Collect per-topic scores
        topic_scores: Dict[str, List[float]] = {}
        for report in reports:
            data = report.data or {}
            for q in data.get("question_breakdown", []):
                topic = q.get("topic") or q.get("question_id", "Unknown")
                tech_score = q.get("technical_score")
                if topic and tech_score is not None:
                    topic_scores.setdefault(topic, []).append(float(tech_score))

        heatmap = []
        for topic, scores in topic_scores.items():
            avg = sum(scores) / len(scores)
            heatmap.append({
                "topic":      topic,
                "avg_score":  round(avg, 1),
                "attempts":   len(scores),
            })

        # Sort by avg_score ascending (weakest areas first)
        return sorted(heatmap, key=lambda x: x["avg_score"])

    # ------------------------------------------------------------------
    # Interview Comparison
    # ------------------------------------------------------------------

    async def get_comparison(
        self,
        user_id: str,
        session_id_a: str,
        session_id_b: str,
    ) -> Dict[str, Any]:
        """
        Side-by-side comparison of two interview sessions.
        """
        result = await self.db.execute(
            select(Report)
            .where(
                Report.user_id     == user_id,
                Report.report_type == "candidate",
                Report.session_id.in_([session_id_a, session_id_b]),
            )
        )
        reports = {r.session_id: r for r in result.scalars().all()}

        def extract(session_id):
            r = reports.get(session_id)
            if not r:
                return None
            data = r.data or {}
            return {
                "session_id":      session_id,
                "readiness_score": data.get("readiness_score", 0),
                "radar_data":      data.get("radar_data", {}),
                "strengths":       data.get("strengths", []),
                "weaknesses":      data.get("weaknesses", []),
            }

        return {
            "session_a": extract(session_id_a),
            "session_b": extract(session_id_b),
        }

    # ------------------------------------------------------------------
    # Summary Stats
    # ------------------------------------------------------------------

    async def get_summary_stats(self, user_id: str) -> Dict[str, Any]:
        """
        Returns high-level summary statistics for the dashboard header.
        """
        history = await self.get_interview_history(user_id, limit=100)
        if not history:
            return {
                "total_interviews":   0,
                "avg_readiness":      0,
                "best_readiness":     0,
                "improvement":        0,
            }

        scores = [h["readiness_score"] for h in history]
        improvement = scores[0] - scores[-1] if len(scores) >= 2 else 0  # latest vs oldest

        return {
            "total_interviews": len(history),
            "avg_readiness":    round(sum(scores) / len(scores), 1),
            "best_readiness":   max(scores),
            "improvement":      round(improvement, 1),
        }
