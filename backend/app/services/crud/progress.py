"""
Resource progress CRUD operations.
"""
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from app.models import ResourceProgress
from app.schemas.resource import ProgressCreate, ProgressUpdate


async def get_progress(db: AsyncSession, progress_id: str) -> Optional[ResourceProgress]:
    """Get progress record by ID"""
    result = await db.execute(
        select(ResourceProgress)
        .where(ResourceProgress.id == progress_id)
        .options(joinedload(ResourceProgress.resource))
    )
    return result.scalar_one_or_none()


async def get_user_progress(
    db: AsyncSession,
    user_id: str,
    resource_id: str
) -> Optional[ResourceProgress]:
    """Get progress for a specific user and resource"""
    result = await db.execute(
        select(ResourceProgress).where(
            and_(
                ResourceProgress.user_id == user_id,
                ResourceProgress.resource_id == resource_id
            )
        )
    )
    return result.scalar_one_or_none()


async def get_user_all_progress(
    db: AsyncSession,
    user_id: str,
    skip: int = 0,
    limit: int = 50,
    is_completed: Optional[bool] = None
) -> List[ResourceProgress]:
    """Get all progress records for a user"""
    query = (
        select(ResourceProgress)
        .where(ResourceProgress.user_id == user_id)
        .options(joinedload(ResourceProgress.resource))
    )
    
    if is_completed is not None:
        query = query.where(ResourceProgress.is_completed == is_completed)
    
    query = query.offset(skip).limit(limit).order_by(ResourceProgress.updated_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_progress(
    db: AsyncSession,
    user_id: str,
    progress_data: ProgressCreate
) -> ResourceProgress:
    """Create a new progress record"""
    progress = ResourceProgress(
        user_id=user_id,
        resource_id=progress_data.resource_id,
        progress_percentage=progress_data.progress_percentage,
        is_completed=progress_data.is_completed,
        time_spent_seconds=progress_data.time_spent_seconds,
        last_position=progress_data.last_position
    )
    db.add(progress)
    await db.flush()
    return progress


async def update_progress(
    db: AsyncSession,
    progress: ResourceProgress,
    progress_data: ProgressUpdate
) -> ResourceProgress:
    """Update a progress record"""
    update_dict = progress_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(progress, field, value)
    
    # Auto-complete if progress reaches 100%
    if progress.progress_percentage >= 100:
        progress.is_completed = True
    
    await db.flush()
    return progress


async def upsert_progress(
    db: AsyncSession,
    user_id: str,
    resource_id: str,
    progress_percentage: float,
    time_spent_seconds: int = 0,
    last_position: Optional[int] = None
) -> ResourceProgress:
    """Create or update progress for a user/resource pair"""
    progress = await get_user_progress(db, user_id, resource_id)
    
    if progress:
        progress.progress_percentage = max(progress.progress_percentage, progress_percentage)
        progress.time_spent_seconds += time_spent_seconds
        if last_position is not None:
            progress.last_position = last_position
        if progress.progress_percentage >= 100:
            progress.is_completed = True
    else:
        progress = ResourceProgress(
            user_id=user_id,
            resource_id=resource_id,
            progress_percentage=progress_percentage,
            is_completed=progress_percentage >= 100,
            time_spent_seconds=time_spent_seconds,
            last_position=last_position
        )
        db.add(progress)
    
    await db.flush()
    return progress


async def delete_progress(db: AsyncSession, progress: ResourceProgress) -> None:
    """Delete a progress record"""
    await db.delete(progress)
    await db.flush()


async def get_completion_stats(db: AsyncSession, user_id: str) -> dict:
    """Get completion statistics for a user"""
    from sqlalchemy import func
    
    # Total resources started
    total_query = select(func.count(ResourceProgress.id)).where(
        ResourceProgress.user_id == user_id
    )
    total_result = await db.execute(total_query)
    total_started = total_result.scalar() or 0
    
    # Resources completed
    completed_query = select(func.count(ResourceProgress.id)).where(
        and_(
            ResourceProgress.user_id == user_id,
            ResourceProgress.is_completed == True
        )
    )
    completed_result = await db.execute(completed_query)
    total_completed = completed_result.scalar() or 0
    
    # Total time spent
    time_query = select(func.sum(ResourceProgress.time_spent_seconds)).where(
        ResourceProgress.user_id == user_id
    )
    time_result = await db.execute(time_query)
    total_time = time_result.scalar() or 0
    
    return {
        "resources_started": total_started,
        "resources_completed": total_completed,
        "total_time_seconds": total_time,
        "completion_rate": round(total_completed / total_started * 100, 1) if total_started > 0 else 0
    }
