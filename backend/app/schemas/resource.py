"""
Learning resource and progress Pydantic schemas.
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# ============= Learning Resource Schemas =============

class ResourceBase(BaseModel):
    """Base resource schema"""
    title: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    resource_type: str = Field(default="Article", pattern='^(Article|Video|Guide|Tutorial)$')
    tags: List[str] = Field(default_factory=list)
    difficulty_level: str = Field(default="beginner", pattern='^(beginner|intermediate|advanced)$')
    estimated_duration: Optional[int] = Field(None, ge=1, description="Duration in minutes")


class ResourceCreate(ResourceBase):
    """Schema for creating a learning resource"""
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    content_body: Optional[str] = None
    video_url: Optional[str] = Field(None, max_length=500)
    slug: Optional[str] = Field(None, max_length=255)
    is_published: bool = True


class ResourceUpdate(BaseModel):
    """Schema for updating a learning resource"""
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    resource_type: Optional[str] = Field(None, pattern='^(Article|Video|Guide|Tutorial)$')
    tags: Optional[List[str]] = None
    thumbnail_url: Optional[str] = Field(None, max_length=500)
    content_body: Optional[str] = None
    video_url: Optional[str] = Field(None, max_length=500)
    difficulty_level: Optional[str] = Field(None, pattern='^(beginner|intermediate|advanced)$')
    estimated_duration: Optional[int] = Field(None, ge=1)
    slug: Optional[str] = Field(None, max_length=255)
    is_published: Optional[bool] = None


class ResourceRead(ResourceBase):
    """Schema for reading a learning resource"""
    id: str
    thumbnail_url: Optional[str] = None
    content_body: Optional[str] = None
    video_url: Optional[str] = None
    slug: Optional[str] = None
    is_published: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ResourceSummary(BaseModel):
    """Summary schema for listing resources"""
    id: str
    title: str
    description: Optional[str] = None
    resource_type: str
    tags: List[str]
    thumbnail_url: Optional[str] = None
    difficulty_level: str
    estimated_duration: Optional[int] = None
    
    class Config:
        from_attributes = True


# ============= Resource Progress Schemas =============

class ProgressBase(BaseModel):
    """Base progress schema"""
    progress_percentage: float = Field(default=0.0, ge=0.0, le=100.0)
    is_completed: bool = False


class ProgressCreate(ProgressBase):
    """Schema for creating progress record"""
    resource_id: str
    time_spent_seconds: int = Field(default=0, ge=0)
    last_position: Optional[int] = None


class ProgressUpdate(BaseModel):
    """Schema for updating progress"""
    progress_percentage: Optional[float] = Field(None, ge=0.0, le=100.0)
    is_completed: Optional[bool] = None
    time_spent_seconds: Optional[int] = Field(None, ge=0)
    last_position: Optional[int] = None


class ProgressRead(ProgressBase):
    """Schema for reading progress"""
    id: str
    user_id: str
    resource_id: str
    time_spent_seconds: int
    last_position: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProgressWithResource(ProgressRead):
    """Progress with embedded resource summary"""
    resource: ResourceSummary
    
    class Config:
        from_attributes = True
