from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import desc

from app.models.reports import Report

async def get_report(db: AsyncSession, report_id: str) -> Optional[Report]:
    query = select(Report).where(Report.id == report_id)
    result = await db.execute(query)
    return result.scalars().first()

async def get_report_by_token(db: AsyncSession, token: str) -> Optional[Report]:
    query = select(Report).where(Report.share_token == token)
    result = await db.execute(query)
    return result.scalars().first()

async def get_user_reports(
    db: AsyncSession, 
    user_id: str, 
    interview_id: Optional[str] = None,
    report_type: Optional[str] = None,
    limit: int = 50, 
    offset: int = 0
) -> List[Report]:
    query = select(Report).where(Report.user_id == user_id)
    if interview_id:
        query = query.where(Report.session_id == interview_id)
    if report_type:
        query = query.where(Report.report_type == report_type)
        
    query = query.order_by(desc(Report.created_at)).limit(limit).offset(offset)
    result = await db.execute(query)
    return result.scalars().all()

async def create_report(db: AsyncSession, user_id: str, session_id: str, report_type: str, data: dict = None) -> Report:
    db_obj = Report(
        user_id=user_id,
        session_id=session_id,
        report_type=report_type,
        data=data or {}
    )
    db.add(db_obj)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def update_report(db: AsyncSession, db_obj: Report, data: dict) -> Report:
    for field, value in data.items():
        setattr(db_obj, field, value)
    await db.commit()
    await db.refresh(db_obj)
    return db_obj

async def delete_report(db: AsyncSession, db_obj: Report):
    await db.delete(db_obj)
    await db.commit()
