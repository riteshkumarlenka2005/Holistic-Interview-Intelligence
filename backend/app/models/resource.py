"""
Learning resource and progress tracking models.
"""
import enum
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, ForeignKey, ARRAY, Index, JSON
from sqlalchemy.orm import relationship

from app.models.base import BaseModel


class ResourceType(str, enum.Enum):
    """Types of learning resources"""
    ARTICLE = "Article"
    VIDEO = "Video"
    GUIDE = "Guide"
    TUTORIAL = "Tutorial"


class DifficultyLevel(str, enum.Enum):
    """Difficulty levels for learning resources"""
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class LearningResource(BaseModel):
    """
    Learning resources for interview preparation.
    Includes articles, videos, guides, and tutorials.
    """
    __tablename__ = "learning_resources"
    
    # Basic info
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    resource_type = Column(String(50), default=ResourceType.ARTICLE.value, nullable=False)
    
    # Tags stored as JSON array for flexibility
    tags = Column(JSON, default=list, nullable=False)
    
    # Media
    thumbnail_url = Column(String(500), nullable=True)
    content_body = Column(Text, nullable=True)
    video_url = Column(String(500), nullable=True)
    
    # Metadata
    difficulty_level = Column(String(20), default=DifficultyLevel.BEGINNER.value, nullable=False)
    estimated_duration = Column(Integer, nullable=True)  # in minutes
    
    # SEO / Discoverability
    slug = Column(String(255), unique=True, nullable=True, index=True)
    is_published = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    progress_records = relationship("ResourceProgress", back_populates="resource", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index("ix_learning_resources_type", "resource_type"),
        Index("ix_learning_resources_difficulty", "difficulty_level"),
        Index("ix_learning_resources_published", "is_published"),
    )
    
    def __repr__(self):
        return f"<LearningResource {self.title}>"


class ResourceProgress(BaseModel):
    """
    Tracks user progress through learning resources.
    """
    __tablename__ = "resource_progress"
    
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    resource_id = Column(String(36), ForeignKey("learning_resources.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Progress tracking
    progress_percentage = Column(Float, default=0.0, nullable=False)
    is_completed = Column(Boolean, default=False, nullable=False)
    
    # Time tracking
    time_spent_seconds = Column(Integer, default=0, nullable=False)
    last_position = Column(Integer, default=0, nullable=True)  # For video resume
    
    # Relationships
    user = relationship("User", back_populates="resource_progress")
    resource = relationship("LearningResource", back_populates="progress_records")
    
    # Indexes and constraints
    __table_args__ = (
        Index("ix_resource_progress_user_resource", "user_id", "resource_id", unique=True),
        Index("ix_resource_progress_completed", "is_completed"),
    )
    
    def __repr__(self):
        return f"<ResourceProgress user={self.user_id} resource={self.resource_id} progress={self.progress_percentage}%>"
