import redis.asyncio as redis
from app.core.config import get_settings

settings = get_settings()
_pool: redis.ConnectionPool = None

async def get_redis_pool() -> redis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=50,
            decode_responses=True,
            socket_keepalive=True,
        )
    return _pool

async def get_redis(db: int = 2) -> redis.Redis:
    pool = await get_redis_pool()
    return redis.Redis(connection_pool=pool, db=db)

# Convenience aliases
async def get_cache_redis() -> redis.Redis:
    return await get_redis(db=2)

async def get_ratelimit_redis() -> redis.Redis:
    return await get_redis(db=3)

async def get_session_redis() -> redis.Redis:
    return await get_redis(db=4)

async def close_redis_pool():
    global _pool
    if _pool is not None:
        await _pool.disconnect()
        _pool = None


def get_redis_client():
    """
    Sync-compatible accessor that returns an async Redis client.
    Used at app startup (middleware setup) where async context is not yet available.
    Returns None if Redis is not reachable; callers must handle None.
    """
    try:
        from app.core.config import get_settings
        settings = get_settings()
        import redis as sync_redis
        client = sync_redis.from_url(settings.REDIS_URL, decode_responses=True)
        client.ping()
        return client
    except Exception:
        return None

