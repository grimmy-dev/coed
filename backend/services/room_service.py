"""
Room management service.

Handles all business logic related to collaborative coding rooms,
including creation, validation, and state management in Redis.
"""

import secrets
from redis.asyncio import Redis

from config.settings import settings


class RoomService:
    """
    Service for managing collaborative coding rooms.

    Responsibilities:
        - Generate unique room IDs
        - Create and initialize rooms
        - Check room existence
        - Manage room state in Redis
        - Handle room TTL (Time-To-Live)
    """

    def __init__(self, redis_client: Redis):
        """
        Initialize room service with Redis client.

        Args:
            redis_client: Redis client instance for data operations
        """
        self.redis = redis_client

    def generate_room_id(self) -> str:
        """
        Generate a cryptographically secure random room ID.

        Returns:
            str: Hexadecimal room ID of configured length
        """
        return secrets.token_hex(settings.room_code_length // 2)

    async def create_room(self) -> tuple[str, bool]:
        """
        Create a new room with a unique ID.

        Handles collision detection by attempting multiple ID generations
        if necessary. Extremely rare with 6-char hex (16M combinations).

        Returns:
            tuple: (room_id, created) where created is True if new room

        Raises:
            Exception: If unable to generate unique ID after max attempts
        """
        max_attempts = 10

        for _ in range(max_attempts):
            room_id = self.generate_room_id()

            # Check if room already exists
            exists = await self.redis.exists(f"room:{room_id}:code")

            if not exists:
                await self._initialize_room(room_id)
                return room_id, True

        raise Exception("Failed to generate unique room ID after multiple attempts")

    async def _initialize_room(self, room_id: str) -> None:
        """
        Initialize room data structure in Redis.

        Creates the code key with TTL. Users set and cursors hash
        are created when first user joins (Redis doesn't store empty collections).

        Args:
            room_id: Room identifier to initialize
        """
        await self.redis.set(
            f"room:{room_id}:code",
            "",  # Start with empty code
            ex=settings.room_ttl_seconds,
        )

    async def room_exists(self, room_id: str) -> bool:
        """
        Check if a room exists in Redis.

        Args:
            room_id: Room identifier to check

        Returns:
            bool: True if room exists, False otherwise
        """
        return bool(await self.redis.exists(f"room:{room_id}:code"))

    async def get_room_code(self, room_id: str) -> str:
        """
        Get current code content for a room.

        Args:
            room_id: Room identifier

        Returns:
            str: Current code content, empty string if not found
        """
        code = await self.redis.get(f"room:{room_id}:code")
        return code if code else ""

    async def refresh_room_ttl(self, room_id: str) -> None:
        """
        Refresh TTL for all room keys.

        Called on room activity to prevent expiration while users are active.

        Args:
            room_id: Room identifier
        """
        ttl = settings.room_ttl_seconds
        await self.redis.expire(f"room:{room_id}:code", ttl)
        await self.redis.expire(f"room:{room_id}:users", ttl)
        await self.redis.expire(f"room:{room_id}:cursors", ttl)
