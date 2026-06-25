"""
Base model classes and mixins for SQLAlchemy models.
Provides common functionality for all database models.
"""
from datetime import datetime, timezone
from typing import Any
import uuid

from sqlalchemy import Column, DateTime, String
from sqlalchemy.orm import declared_attr, DeclarativeBase
from sqlalchemy.sql import func


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.
    Provides common metadata and configuration.
    """
    # Allow legacy Column-based annotations without Mapped[] wrapper
    __allow_unmapped__ = True


class UUIDMixin:
    """
    Mixin providing UUID primary key.
    Uses string representation of UUID for database compatibility.
    """
    @declared_attr
    def id(cls):
        return Column(
            String(36), 
            primary_key=True, 
            default=lambda: str(uuid.uuid4()),
            nullable=False
        )


class TimestampMixin:
    """
    Mixin providing created_at and updated_at timestamp fields.
    Timestamps are timezone-aware (UTC).
    """
    @declared_attr
    def created_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            nullable=False
        )
    
    @declared_attr
    def updated_at(cls):
        return Column(
            DateTime(timezone=True),
            server_default=func.now(),
            onupdate=func.now(),
            nullable=False
        )


class BaseModel(Base, UUIDMixin, TimestampMixin):
    """
    Abstract base model with UUID primary key and timestamps.
    All domain models should inherit from this class.
    
    Provides:
    - id: UUID primary key (string format)
    - created_at: Timezone-aware creation timestamp
    - updated_at: Timezone-aware update timestamp
    """
    __abstract__ = True
    
    def to_dict(self) -> dict[str, Any]:
        """Convert model instance to dictionary"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def __repr__(self) -> str:
        """Default string representation"""
        return f"<{self.__class__.__name__}(id={self.id})>"
