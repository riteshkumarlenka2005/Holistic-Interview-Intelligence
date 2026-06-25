"""
Database connection and session management
Supports both PostgreSQL (production) and SQLite (development)
"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import text
from app.core.config import get_settings

# Import Base from models package (this is the source of truth for Base)
from app.models.base import Base

settings = get_settings()


def _create_engine():
    """Create async engine with appropriate settings for the database type"""
    # Base engine arguments
    engine_args = {
        "echo": settings.db_echo or settings.debug,
        "future": True,
    }
    
    # PostgreSQL-specific settings (connection pooling)
    if settings.is_postgres:
        engine_args.update({
            "pool_pre_ping": True,
            "pool_size": settings.database_pool_size,
            "max_overflow": settings.database_max_overflow,
            "pool_timeout": settings.database_pool_timeout,
            "pool_recycle": settings.database_pool_recycle,
        })
    # SQLite doesn't support connection pooling the same way
    elif settings.is_sqlite:
        engine_args.update({
            "connect_args": {"check_same_thread": False},
        })
    
    return create_async_engine(settings.database_url, **engine_args)


# Create async engine
engine = _create_engine()

# Session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

# Re-export Base for convenience (source is models.base)
__all__ = ["engine", "AsyncSessionLocal", "Base", "get_db", "init_db", "check_db_health", "dispose_engine"]


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency for getting database sessions.
    Yields session and handles commit/rollback automatically.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def init_db():
    """Initialize database tables (creates all tables if they don't exist)"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def check_db_health() -> dict:
    """
    Check database connectivity and return health status.
    Used for health check endpoints.
    """
    try:
        async with AsyncSessionLocal() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalar()
        return {
            "status": "healthy",
            "database": "connected",
            "type": "postgresql" if settings.is_postgres else "sqlite"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "database": "disconnected",
            "error": str(e)
        }


async def dispose_engine():
    """Dispose of the engine connection pool (for graceful shutdown)"""
    await engine.dispose()
