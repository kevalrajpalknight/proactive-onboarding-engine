"""Redis connection manager for pub/sub and caching."""

import redis.asyncio as aioredis
import structlog

from .config import settings

logger = structlog.get_logger()

# ---------------------------------------------------------------------------
# Connection pool (shared across the application)
# ---------------------------------------------------------------------------
_pool: aioredis.ConnectionPool | None = None


def _get_pool() -> aioredis.ConnectionPool:
    global _pool
    if _pool is None:
        _pool = aioredis.ConnectionPool.from_url(
            settings.redis_url,
            decode_responses=True,
            max_connections=20,
        )
    return _pool


def get_redis() -> aioredis.Redis:
    """Return an async Redis client backed by the shared pool."""
    return aioredis.Redis(connection_pool=_get_pool())


async def close_redis() -> None:
    """Gracefully close the connection pool (call on app shutdown)."""
    global _pool
    if _pool is not None:
        await _pool.aclose()
        _pool = None
        logger.info("redis_pool_closed")


# ---------------------------------------------------------------------------
# Pub/Sub channel helpers
# ---------------------------------------------------------------------------
ROADMAP_CHANNEL_PREFIX = "roadmap:progress:"


def roadmap_channel(session_id: str) -> str:
    """Return the Redis channel name for a given session's roadmap progress."""
    return f"{ROADMAP_CHANNEL_PREFIX}{session_id}"


# ---------------------------------------------------------------------------
# Progress key helpers (for reconnection / catch-up)
# ---------------------------------------------------------------------------
ROADMAP_STATE_PREFIX = "roadmap:state:"


def roadmap_state_key(session_id: str) -> str:
    """Return the Redis key that stores the latest progress state."""
    return f"{ROADMAP_STATE_PREFIX}{session_id}"
