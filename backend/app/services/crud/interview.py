"""
Interview session CRUD operations.
"""
from typing import Optional, List
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import InterviewSession, SessionStatus
from app.schemas.interview import SessionCreate, SessionUpdate


async def get_session(db: AsyncSession, session_id: str) -> Optional[InterviewSession]:
    """Get interview session by ID"""
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.id == session_id)
        .options(joinedload(InterviewSession.analysis))
    )
    return result.scalar_one_or_none()


async def get_user_sessions(
    db: AsyncSession,
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    status: Optional[str] = None,
    session_type: Optional[str] = None
) -> List[InterviewSession]:
    """Get all sessions for a user"""
    query = select(InterviewSession).where(InterviewSession.user_id == user_id)
    
    if status:
        query = query.where(InterviewSession.status == status)
    if session_type:
        query = query.where(InterviewSession.session_type == session_type)
    
    query = query.offset(skip).limit(limit).order_by(InterviewSession.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_session(
    db: AsyncSession,
    user_id: str,
    session_data: SessionCreate
) -> InterviewSession:
    """Create a new interview session"""
    session = InterviewSession(
        user_id=user_id,
        title=session_data.title,
        session_type=session_data.session_type,
        target_job_role=session_data.target_job_role,
        target_company=session_data.target_company,
        duration_minutes=session_data.duration_minutes,
        questions=session_data.questions,
        notes=session_data.notes,
        status=SessionStatus.DRAFT.value
    )
    db.add(session)
    await db.flush()
    return session


async def update_session(
    db: AsyncSession,
    session: InterviewSession,
    session_data: SessionUpdate
) -> InterviewSession:
    """Update an interview session"""
    update_dict = session_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(session, field, value)
    await db.flush()
    return session


async def start_session(db: AsyncSession, session: InterviewSession) -> InterviewSession:
    """Mark session as started"""
    session.status = SessionStatus.IN_PROGRESS.value
    session.started_at = datetime.now()
    await db.flush()
    return session


async def complete_session(db: AsyncSession, session: InterviewSession) -> InterviewSession:
    """Mark session as completed"""
    session.status = SessionStatus.COMPLETED.value
    session.ended_at = datetime.now()
    await db.flush()
    return session


async def archive_session(db: AsyncSession, session: InterviewSession) -> InterviewSession:
    """Archive a session"""
    session.status = SessionStatus.ARCHIVED.value
    await db.flush()
    return session


async def add_question(
    db: AsyncSession,
    session: InterviewSession,
    question: str
) -> InterviewSession:
    """Add a question to the session"""
    questions = session.questions or []
    questions.append(question)
    session.questions = questions
    await db.flush()
    return session


async def add_response(
    db: AsyncSession,
    session: InterviewSession,
    question_index: int,
    response_text: Optional[str] = None,
    audio_url: Optional[str] = None,
    video_url: Optional[str] = None,
    duration_seconds: Optional[float] = None
) -> InterviewSession:
    """Add a response to a question"""
    responses = session.responses or []
    
    # Validate question index
    if question_index >= len(session.questions or []):
        raise ValueError("Invalid question index")
    
    response = {
        "question_index": question_index,
        "question_text": session.questions[question_index],
        "response_text": response_text,
        "audio_url": audio_url,
        "video_url": video_url,
        "duration_seconds": duration_seconds,
        "recorded_at": datetime.now().isoformat()
    }
    responses.append(response)
    session.responses = responses
    await db.flush()
    return session


async def delete_session(db: AsyncSession, session: InterviewSession) -> None:
    """Delete an interview session"""
    await db.delete(session)
    await db.flush()


async def get_session_stats(db: AsyncSession, user_id: str) -> dict:
    """Get interview statistics for a user"""
    from sqlalchemy import func
    
    # Total sessions
    total_query = select(func.count(InterviewSession.id)).where(
        InterviewSession.user_id == user_id
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0
    
    # Completed sessions
    completed_query = select(func.count(InterviewSession.id)).where(
        and_(
            InterviewSession.user_id == user_id,
            InterviewSession.status.in_([SessionStatus.COMPLETED.value, SessionStatus.ANALYZED.value])
        )
    )
    completed_result = await db.execute(completed_query)
    completed = completed_result.scalar() or 0
    
    # Analyzed sessions
    analyzed_query = select(func.count(InterviewSession.id)).where(
        and_(
            InterviewSession.user_id == user_id,
            InterviewSession.status == SessionStatus.ANALYZED.value
        )
    )
    analyzed_result = await db.execute(analyzed_query)
    analyzed = analyzed_result.scalar() or 0
    
    return {
        "total_sessions": total,
        "completed_sessions": completed,
        "analyzed_sessions": analyzed,
        "completion_rate": round(completed / total * 100, 1) if total > 0 else 0
    }
