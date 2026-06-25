from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.models.jobs import AnalysisJob

async def get_job(db: AsyncSession, job_id: str) -> Optional[AnalysisJob]:
    query = select(AnalysisJob).where(AnalysisJob.id == job_id)
    result = await db.execute(query)
    return result.scalars().first()

async def get_job_by_celery_task(db: AsyncSession, task_id: str) -> Optional[AnalysisJob]:
    query = select(AnalysisJob).where(AnalysisJob.celery_task_id == task_id)
    result = await db.execute(query)
    return result.scalars().first()

async def get_jobs_by_session(db: AsyncSession, session_id: str) -> List[AnalysisJob]:
    query = select(AnalysisJob).where(AnalysisJob.session_id == session_id).order_by(desc(AnalysisJob.created_at))
    result = await db.execute(query)
    return result.scalars().all()

async def list_jobs(db: AsyncSession, status: Optional[str] = None, limit: int = 20) -> List[AnalysisJob]:
    query = select(AnalysisJob)
    if status:
        query = query.where(AnalysisJob.status == status)
    query = query.order_by(desc(AnalysisJob.created_at)).limit(limit)
    result = await db.execute(query)
    return result.scalars().all()

async def create_job(db: AsyncSession, session_id: str, job_type: str, data: dict = None) -> AnalysisJob:
    db_obj = AnalysisJob(
        session_id=session_id,
        job_type=job_type,
        status="pending",
        progress=0,
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_job(db: AsyncSession, db_obj: AnalysisJob, data: dict) -> AnalysisJob:
    for field, value in data.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_job(db: AsyncSession, db_obj: AnalysisJob):
    await db.delete(db_obj)
    await db.commit()
