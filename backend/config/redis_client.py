"""
Redis client singleton for shared connection pool across the app.
"""

from typing import Optional

import redis.asyncio as redis

from config.settings import settings


class RedisClient:
    """
    Singleton Redis client - ensures only one connection pool exists.
    Improves performance by reusing connections instead of creating new ones.
    """

    _instance: Optional[redis.Redis] = None

    @classmethod
    async def get_client(cls) -> redis.Redis:
        """
        Get or create Redis client instance.
        Thread-safe singleton pattern.
        """
        if cls._instance is None:
            cls._instance = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,  # Automatically decode bytes to strings
            )
        return cls._instance

    @classmethod
    async def close(cls) -> None:
        """
        Close Redis connection pool on shutdown.
        Call this during application cleanup.
        """
        if cls._instance:
            await cls._instance.close()
            cls._instance = None


async def get_redis() -> redis.Redis:
    """
    FastAPI dependency for injecting Redis into routes.

    Usage:
        @router.get("/example")
        async def example(redis: Redis = Depends(get_redis)):
            ...
    """
    return await RedisClient.get_client()
