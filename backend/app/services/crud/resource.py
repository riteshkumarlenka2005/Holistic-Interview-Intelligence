"""
Learning resource CRUD operations.
"""
from typing import Optional, List
from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import LearningResource
from app.schemas.resource import ResourceCreate, ResourceUpdate


async def get_resource(db: AsyncSession, resource_id: str) -> Optional[LearningResource]:
    """Get resource by ID"""
    result = await db.execute(
        select(LearningResource).where(LearningResource.id == resource_id)
    )
    return result.scalar_one_or_none()


async def get_resource_by_slug(db: AsyncSession, slug: str) -> Optional[LearningResource]:
    """Get resource by slug"""
    result = await db.execute(
        select(LearningResource).where(LearningResource.slug == slug)
    )
    return result.scalar_one_or_none()


async def get_resources(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 50,
    resource_type: Optional[str] = None,
    difficulty_level: Optional[str] = None,
    is_published: Optional[bool] = True,
    search: Optional[str] = None
) -> List[LearningResource]:
    """Get list of resources with filtering"""
    query = select(LearningResource)
    
    if is_published is not None:
        query = query.where(LearningResource.is_published == is_published)
    if resource_type:
        query = query.where(LearningResource.resource_type == resource_type)
    if difficulty_level:
        query = query.where(LearningResource.difficulty_level == difficulty_level)
    if search:
        search_pattern = f"%{search}%"
        query = query.where(
            or_(
                LearningResource.title.ilike(search_pattern),
                LearningResource.description.ilike(search_pattern)
            )
        )
    
    query = query.offset(skip).limit(limit).order_by(LearningResource.created_at.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_resource(db: AsyncSession, resource_data: ResourceCreate) -> LearningResource:
    """Create a new learning resource"""
    resource = LearningResource(**resource_data.model_dump())
    db.add(resource)
    await db.flush()
    return resource


async def update_resource(
    db: AsyncSession, 
    resource: LearningResource, 
    resource_data: ResourceUpdate
) -> LearningResource:
    """Update a learning resource"""
    update_dict = resource_data.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(resource, field, value)
    await db.flush()
    return resource


async def delete_resource(db: AsyncSession, resource: LearningResource) -> None:
    """Delete a learning resource"""
    await db.delete(resource)
    await db.flush()


async def get_resources_by_tags(
    db: AsyncSession, 
    tags: List[str], 
    limit: int = 20
) -> List[LearningResource]:
    """Get resources that contain any of the specified tags"""
    # Using PostgreSQL JSONB array containment
    from sqlalchemy.dialects.postgresql import JSONB
    from sqlalchemy import any_
    
    results = []
    query = (
        select(LearningResource)
        .where(LearningResource.is_published == True)
        .limit(limit)
    )
    result = await db.execute(query)
    resources = result.scalars().all()
    
    # Filter by tags (in-memory for cross-DB compatibility)
    for resource in resources:
        if resource.tags and any(tag in resource.tags for tag in tags):
            results.append(resource)
    
    return results[:limit]


async def count_resources(
    db: AsyncSession,
    resource_type: Optional[str] = None,
    is_published: Optional[bool] = True
) -> int:
    """Count total resources"""
    from sqlalchemy import func
    query = select(func.count(LearningResource.id))
    if is_published is not None:
        query = query.where(LearningResource.is_published == is_published)
    if resource_type:
        query = query.where(LearningResource.resource_type == resource_type)
    result = await db.execute(query)
    return result.scalar() or 0
