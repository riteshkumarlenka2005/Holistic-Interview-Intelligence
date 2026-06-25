"""
Interview analysis CRUD operations.
"""
from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import InterviewAnalysis, InterviewSession, SessionStatus
from app.schemas.interview import AnalysisCreate, AnalysisUpdate


async def get_analysis(db: AsyncSession, analysis_id: str) -> Optional[InterviewAnalysis]:
    """Get analysis by ID"""
    result = await db.execute(
        select(InterviewAnalysis).where(InterviewAnalysis.id == analysis_id)
    )
    return result.scalar_one_or_none()


async def get_analysis_by_session(db: AsyncSession, session_id: str) -> Optional[InterviewAnalysis]:
    """Get analysis by session ID"""
    result = await db.execute(
        select(InterviewAnalysis).where(InterviewAnalysis.session_id == session_id)
    )
    return result.scalar_one_or_none()


async def create_analysis(
    db: AsyncSession,
    analysis_data: AnalysisCreate
) -> InterviewAnalysis:
    """Create a new analysis record"""
    analysis = InterviewAnalysis(
        session_id=analysis_data.session_id,
        verbal_metrics=analysis_data.verbal_metrics,
        nonverbal_metrics=analysis_data.nonverbal_metrics,
        multimodal_score=analysis_data.multimodal_score,
        recommendations=analysis_data.recommendations,
        analysis_version=analysis_data.analysis_version,
        processing_time_seconds=analysis_data.processing_time_seconds,
        explainability=analysis_data.explainability
    )
    db.add(analysis)
    await db.flush()
    
    # Update session status to analyzed
    session_result = await db.execute(
        select(InterviewSession).where(InterviewSession.id == analysis_data.session_id)
    )
    session = session_result.scalar_one_or_none()
    if session:
        session.status = SessionStatus.ANALYZED.value
    
    return analysis


async def update_analysis(
    db: AsyncSession,
    analysis: InterviewAnalysis,
    analysis_data: AnalysisUpdate
) -> InterviewAnalysis:
    """Update an analysis record"""
    update_dict = analysis_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(analysis, field, value)
    await db.flush()
    return analysis


async def append_verbal_metrics(
    db: AsyncSession,
    analysis: InterviewAnalysis,
    new_metrics: dict
) -> InterviewAnalysis:
    """Append new metrics to verbal_metrics JSONB field"""
    current = analysis.verbal_metrics or {}
    current.update(new_metrics)
    analysis.verbal_metrics = current
    await db.flush()
    return analysis


async def append_nonverbal_metrics(
    db: AsyncSession,
    analysis: InterviewAnalysis,
    new_metrics: dict
) -> InterviewAnalysis:
    """Append new metrics to nonverbal_metrics JSONB field"""
    current = analysis.nonverbal_metrics or {}
    current.update(new_metrics)
    analysis.nonverbal_metrics = current
    await db.flush()
    return analysis


async def update_multimodal_score(
    db: AsyncSession,
    analysis: InterviewAnalysis,
    scores: dict
) -> InterviewAnalysis:
    """Update multimodal fusion scores"""
    current = analysis.multimodal_score or {}
    current.update(scores)
    analysis.multimodal_score = current
    await db.flush()
    return analysis


async def add_recommendations(
    db: AsyncSession,
    analysis: InterviewAnalysis,
    recommendations: dict
) -> InterviewAnalysis:
    """Add or update recommendations"""
    current = analysis.recommendations or {}
    current.update(recommendations)
    analysis.recommendations = current
    await db.flush()
    return analysis


async def delete_analysis(db: AsyncSession, analysis: InterviewAnalysis) -> None:
    """Delete an analysis record"""
    # Revert session status
    session_result = await db.execute(
        select(InterviewSession).where(InterviewSession.id == analysis.session_id)
    )
    session = session_result.scalar_one_or_none()
    if session and session.status == SessionStatus.ANALYZED.value:
        session.status = SessionStatus.COMPLETED.value
    
    await db.delete(analysis)
    await db.flush()


async def get_user_analyses(
    db: AsyncSession,
    user_id: str,
    skip: int = 0,
    limit: int = 20
) -> List[InterviewAnalysis]:
    """Get all analyses for a user's sessions"""
    query = (
        select(InterviewAnalysis)
        .join(InterviewSession)
        .where(InterviewSession.user_id == user_id)
        .offset(skip)
        .limit(limit)
        .order_by(InterviewAnalysis.created_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_average_scores(db: AsyncSession, user_id: str) -> dict:
    """Get average scores across all user's analyses"""
    analyses = await get_user_analyses(db, user_id, limit=100)
    
    if not analyses:
        return {
            "average_confidence": None,
            "average_communication": None,
            "average_engagement": None,
            "total_analyses": 0
        }
    
    confidence_scores = []
    communication_scores = []
    engagement_scores = []
    
    for analysis in analyses:
        if analysis.multimodal_score:
            if "combined_confidence" in analysis.multimodal_score:
                confidence_scores.append(analysis.multimodal_score["combined_confidence"])
            if "communication_score" in analysis.multimodal_score:
                communication_scores.append(analysis.multimodal_score["communication_score"])
            if "engagement_score" in analysis.multimodal_score:
                engagement_scores.append(analysis.multimodal_score["engagement_score"])
    
    return {
        "average_confidence": round(sum(confidence_scores) / len(confidence_scores), 2) if confidence_scores else None,
        "average_communication": round(sum(communication_scores) / len(communication_scores), 2) if communication_scores else None,
        "average_engagement": round(sum(engagement_scores) / len(engagement_scores), 2) if engagement_scores else None,
        "total_analyses": len(analyses)
    }
