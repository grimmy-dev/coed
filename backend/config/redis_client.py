"""
Redis client singleton for application-wide database access.

Provides a single Redis connection pool shared across all services.
"""

from typing import Optional

import redis.asyncio as redis

from config.settings import settings


class RedisClient:
    """
    Singleton Redis client manager.

    Ensures only one Redis connection pool exists throughout the application
    lifecycle, improving performance and resource management.
    """

    _instance: Optional[redis.Redis] = None

    @classmethod
    async def get_client(cls) -> redis.Redis:
        """
        Get or create Redis client instance.

        Returns:
            redis.Redis: Configured Redis client with connection pool
        """
        if cls._instance is None:
            cls._instance = redis.from_url(
                settings.redis_url,
                encoding="utf-8",
                decode_responses=True,
            )
        return cls._instance

    @classmethod
    async def close(cls) -> None:
        """
        Close Redis connection pool.

        Should be called during application shutdown to ensure
        all connections are properly closed.
        """
        if cls._instance:
            await cls._instance.close()
            cls._instance = None


async def get_redis() -> redis.Redis:
    """
    Dependency injection function for FastAPI routes.

    Returns:
        redis.Redis: Active Redis client instance
    """
    return await RedisClient.get_client()
