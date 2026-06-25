"""
Interview management API endpoints
Full implementation with database session management
"""
from fastapi import APIRouter, HTTPException, Depends, Query, Path
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.dependencies import get_current_user
from app.models.user import User
from app.schemas.interview import (
    SessionCreate, SessionUpdate, SessionRead, SessionSummary,
    AddQuestionRequest, AddResponseRequest, QuestionResponse,
    IntegrityEventCreate, IntegrityEventRead
)
from app.models.integrity import IntegrityEvent
from app.services.crud import interview as crud_interview

router = APIRouter()


@router.get("/", response_model=List[SessionSummary])
async def list_interviews(
    status: Optional[str] = Query(None, description="Filter by status"),
    session_type: Optional[str] = Query(None, description="Filter by session type"),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """List user's interviews with optional filtering"""
    sessions = await crud_interview.get_user_sessions(
        db=db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        status=status,
        session_type=session_type
    )
    return sessions


@router.post("/", response_model=SessionRead, status_code=201)
async def create_interview(
    request: SessionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new interview session"""
    session = await crud_interview.create_session(
        db=db,
        user_id=current_user.id,
        session_data=request
    )
    return session


@router.get("/{interview_id}", response_model=SessionRead)
async def get_interview(
    interview_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get interview details"""
    session = await crud_interview.get_session(db=db, session_id=interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    return session


@router.patch("/{interview_id}", response_model=SessionRead)
async def update_interview(
    request: SessionUpdate,
    interview_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update interview details"""
    session = await crud_interview.get_session(db=db, session_id=interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    updated_session = await crud_interview.update_session(db=db, session=session, session_data=request)
    return updated_session


@router.post("/{interview_id}/start", response_model=SessionRead)
async def start_interview(
    interview_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark interview as in progress"""
    session = await crud_interview.get_session(db=db, session_id=interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    started_session = await crud_interview.start_session(db=db, session=session)
    return started_session


@router.post("/{interview_id}/complete", response_model=SessionRead)
async def complete_interview(
    interview_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark interview as completed"""
    session = await crud_interview.get_session(db=db, session_id=interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    completed_session = await crud_interview.complete_session(db=db, session=session)
    return completed_session


@router.post("/{interview_id}/questions", response_model=SessionRead)
async def add_question(
    request: AddQuestionRequest,
    interview_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a question to the interview"""
    session = await crud_interview.get_session(db=db, session_id=interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    updated_session = await crud_interview.add_question(db=db, session=session, question=request.question)
    return updated_session


@router.post("/{interview_id}/responses", response_model=SessionRead)
async def add_response(
    request: AddResponseRequest,
    interview_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a response to a question"""
    session = await crud_interview.get_session(db=db, session_id=interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    try:
        updated_session = await crud_interview.add_response(
            db=db,
            session=session,
            question_index=request.question_index,
            response_text=request.response_text,
            audio_url=request.audio_url,
            video_url=request.video_url,
            duration_seconds=request.duration_seconds
        )
        return updated_session
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{interview_id}")
async def delete_interview(
    interview_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete an interview"""
    session = await crud_interview.get_session(db=db, session_id=interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    await crud_interview.delete_session(db=db, session=session)
    return {"message": "Interview deleted", "interview_id": interview_id}


@router.post("/{interview_id}/events", response_model=IntegrityEventRead, status_code=201)
async def add_integrity_event(
    request: IntegrityEventCreate,
    interview_id: str = Path(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Report a browser or vision integrity event (tab switch, blur, etc.)"""
    session = await crud_interview.get_session(db=db, session_id=interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    event = IntegrityEvent(
        session_id=interview_id,
        event_type=request.event_type,
        timestamp_ms=request.timestamp_ms,
        details=request.details
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)
    
    return event


@router.get("/{interview_id}/export")
async def export_interview(
    interview_id: str = Path(...),
    format: str = Query("json", pattern="^(json)$"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Export interview data"""
    session = await crud_interview.get_session(db=db, session_id=interview_id)
    if not session:
        raise HTTPException(status_code=404, detail="Interview not found")
    if session.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this interview")
    
    return session
