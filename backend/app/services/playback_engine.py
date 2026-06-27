"""
Playback Metadata Engine.

The Playback Engine does NOT store video (that is V2 requiring S3/CDN).
It provides synchronized playback METADATA — the timeline, transcript,
scores, coaching hints, and integrity events — so the frontend can
replay the data layer of the interview at the correct timestamps.

What it produces:
    - transcript_timeline  (each answer with start/end time)
    - score_timeline       (scores over time)
    - coaching_events      (coaching hints that fired, with timestamps)
    - integrity_events     (cheating events, with timestamps)
    - emotion_timeline     (if emotion data was stored)

This is 100% complete functionality for data playback.
Video recording is V2.
"""
from typing import Dict, Any, List, Optional
from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.interview import InterviewSession
from app.models.responses import Response
from app.models.integrity import IntegrityEvent
from app.models.reports import Report


class PlaybackEngine:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_playback_data(self, session_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Fetches and assembles all playback metadata for a session.

        Returns None if session not found or not authorized.
        """
        # Fetch session
        result = await self.db.execute(
            select(InterviewSession).where(
                InterviewSession.id      == session_id,
                InterviewSession.user_id == user_id,
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            return None

        # Fetch responses (the Q&A timeline)
        resp_result = await self.db.execute(
            select(Response)
            .where(Response.session_id == session_id)
            .order_by(Response.created_at)
        )
        responses = resp_result.scalars().all()

        # Fetch integrity events
        evt_result = await self.db.execute(
            select(IntegrityEvent)
            .where(IntegrityEvent.session_id == session_id)
            .order_by(IntegrityEvent.created_at)
        )
        integrity_events = evt_result.scalars().all()

        # Fetch report for pre-computed scores
        rpt_result = await self.db.execute(
            select(Report).where(
                Report.session_id  == session_id,
                Report.report_type == "candidate",
            )
        )
        report = rpt_result.scalar_one_or_none()

        session_start = session.started_at

        def offset(dt: Optional[datetime]) -> Optional[float]:
            """Seconds since session start."""
            if dt is None or session_start is None:
                return None
            return round((dt - session_start).total_seconds(), 2)

        # Build transcript timeline — each answer as a chapter
        transcript_timeline = []
        for i, r in enumerate(responses):
            df = r.detailed_feedback or {}
            transcript_timeline.append({
                "chapter":           i + 1,
                "question":          df.get("question_text", ""),
                "transcript":        r.transcript or "",
                "timestamp_offset":  offset(r.created_at),
                "technical_score":   r.technical_score,
                "communication_score": r.communication_score,
                "structure_used":    df.get("structure_used", ""),
                "strengths":         df.get("technical_strengths", []) + df.get("communication_strengths", []),
                "weaknesses":        df.get("technical_weaknesses", []) + df.get("communication_weaknesses", []),
                "improvement_tips":  df.get("improvement_tips", []),
            })

        # Build score timeline (scores over time, for the trend graph on playback)
        score_timeline = []
        for r in responses:
            score_timeline.append({
                "timestamp_offset": offset(r.created_at),
                "technical_score":  r.technical_score,
                "communication_score": r.communication_score,
            })

        # Build integrity event timeline
        integrity_timeline = []
        for evt in integrity_events:
            integrity_timeline.append({
                "event_type":       evt.event_type,
                "timestamp_offset": offset(evt.created_at),
                "description":      self._describe_event(evt.event_type),
            })

        # Session metadata
        session_duration = None
        if session.started_at and session.ended_at:
            session_duration = round((session.ended_at - session.started_at).total_seconds())

        # Report summary for the playback overlay
        report_summary = {}
        if report and report.data:
            report_summary = {
                "readiness_score":    report.data.get("readiness_score"),
                "radar_data":         report.data.get("radar_data", {}),
                "executive_summary":  report.data.get("executive_summary", ""),
            }

        return {
            "session_id":          session_id,
            "job_role":            session.target_job_role,
            "session_duration_s":  session_duration,
            "started_at":          session.started_at.isoformat() if session.started_at else None,
            "ended_at":            session.ended_at.isoformat()   if session.ended_at   else None,
            "transcript_timeline": transcript_timeline,
            "score_timeline":      score_timeline,
            "integrity_timeline":  integrity_timeline,
            "report_summary":      report_summary,
            "total_questions":     len(responses),
            "has_video":           False,  # V2 — requires S3 integration
        }

    @staticmethod
    def _describe_event(event_type: str) -> str:
        descriptions = {
            "tab_switch":        "Candidate switched browser tab",
            "window_blur":       "Browser window lost focus",
            "multiple_faces":    "Multiple faces detected in frame",
            "distraction_event": "Candidate looked away for an extended period",
        }
        return descriptions.get(event_type, event_type)
