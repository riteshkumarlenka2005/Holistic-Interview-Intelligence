"""
Learning resources API endpoints.
Full CRUD with progress tracking.
"""
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models import User, LearningResource
from app.schemas.resource import (
    ResourceCreate,
    ResourceUpdate,
    ResourceRead,
    ResourceSummary,
    ProgressCreate,
    ProgressUpdate,
    ProgressRead,
    ProgressWithResource,
)
from app.services.crud import (
    get_resource,
    get_resource_by_slug,
    get_resources,
    create_resource,
    update_resource,
    delete_resource,
    count_resources,
    get_user_progress,
    get_user_all_progress,
    upsert_progress,
    get_completion_stats,
)

router = APIRouter()


# ============= Learning Resources =============

@router.get("/", response_model=List[ResourceSummary])
async def list_resources(
    resource_type: Optional[str] = Query(None, description="Filter by type: Article, Video, Guide, Tutorial"),
    difficulty_level: Optional[str] = Query(None, description="Filter by level: beginner, intermediate, advanced"),
    search: Optional[str] = Query(None, description="Search in title and description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """List all published learning resources with optional filtering"""
    resources = await get_resources(
        db,
        skip=skip,
        limit=limit,
        resource_type=resource_type,
        difficulty_level=difficulty_level,
        is_published=True,
        search=search
    )
    return resources


@router.get("/count")
async def get_resource_count(
    resource_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get total count of published resources"""
    count = await count_resources(db, resource_type=resource_type, is_published=True)
    return {"count": count}


@router.get("/{resource_id}", response_model=ResourceRead)
async def get_resource_detail(
    resource_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get resource details by ID"""
    resource = await get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    if not resource.is_published:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.get("/slug/{slug}", response_model=ResourceRead)
async def get_resource_by_slug_endpoint(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get resource by URL slug"""
    resource = await get_resource_by_slug(db, slug)
    if not resource or not resource.is_published:
        raise HTTPException(status_code=404, detail="Resource not found")
    return resource


@router.post("/", response_model=ResourceRead, status_code=201)
async def create_new_resource(
    resource_data: ResourceCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new learning resource (admin/coach only)"""
    if current_user.role not in ["admin", "coach"]:
        raise HTTPException(status_code=403, detail="Only admins and coaches can create resources")
    
    resource = await create_resource(db, resource_data)
    return resource


@router.patch("/{resource_id}", response_model=ResourceRead)
async def update_existing_resource(
    resource_id: str,
    resource_data: ResourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update a learning resource (admin/coach only)"""
    if current_user.role not in ["admin", "coach"]:
        raise HTTPException(status_code=403, detail="Only admins and coaches can update resources")
    
    resource = await get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    updated = await update_resource(db, resource, resource_data)
    return updated


@router.delete("/{resource_id}")
async def delete_existing_resource(
    resource_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a learning resource (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can delete resources")
    
    resource = await get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    await delete_resource(db, resource)
    return {"message": "Resource deleted", "resource_id": resource_id}


# ============= Progress Tracking =============

@router.get("/progress/me", response_model=List[ProgressRead])
async def get_my_progress(
    is_completed: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user's progress on all resources"""
    progress = await get_user_all_progress(
        db,
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        is_completed=is_completed
    )
    return progress


@router.get("/progress/me/stats")
async def get_my_progress_stats(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get completion statistics for current user"""
    stats = await get_completion_stats(db, current_user.id)
    return stats


@router.get("/progress/{resource_id}", response_model=Optional[ProgressRead])
async def get_resource_progress(
    resource_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get progress for a specific resource"""
    progress = await get_user_progress(db, current_user.id, resource_id)
    if not progress:
        return None
    return progress


@router.post("/progress/{resource_id}", response_model=ProgressRead)
async def update_resource_progress(
    resource_id: str,
    progress_percentage: float = Query(..., ge=0, le=100),
    time_spent_seconds: int = Query(0, ge=0),
    last_position: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update progress for a resource (creates if doesn't exist)"""
    # Verify resource exists
    resource = await get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    progress = await upsert_progress(
        db,
        user_id=current_user.id,
        resource_id=resource_id,
        progress_percentage=progress_percentage,
        time_spent_seconds=time_spent_seconds,
        last_position=last_position
    )
    return progress


@router.post("/progress/{resource_id}/complete", response_model=ProgressRead)
async def mark_resource_complete(
    resource_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Mark a resource as complete"""
    resource = await get_resource(db, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    progress = await upsert_progress(
        db,
        user_id=current_user.id,
        resource_id=resource_id,
        progress_percentage=100.0
    )
    return progress
