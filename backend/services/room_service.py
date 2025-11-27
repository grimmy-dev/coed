"""
Room management service - handles room lifecycle and state.
"""

import secrets
from redis.asyncio import Redis

from config.settings import settings


class RoomService:
    """
    Manages collaborative coding rooms in Redis.

    Responsibilities:
        - Generate unique room IDs
        - Create and initialize rooms
        - Check room existence
        - Manage room TTL (expiration)
    """

    def __init__(self, redis_client: Redis):
        """Initialize with Redis client."""
        self.redis = redis_client

    def generate_room_id(self) -> str:
        """
        Generate cryptographically secure random room ID.
        6 chars = 16 million combinations (collision extremely rare).
        """
        return secrets.token_hex(settings.room_code_length // 2)

    async def create_room(self) -> tuple[str, bool]:
        """
        Create a new room with unique ID.

        Handles collision detection by retrying if ID already exists.
        Returns (room_id, created) tuple.
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
        Initialize room in Redis with empty code.
        Sets TTL so room expires after inactivity.
        """
        await self.redis.set(
            f"room:{room_id}:code",
            "",  # Start with empty code
            ex=settings.room_ttl_seconds,  # Auto-expire after TTL
        )

    async def room_exists(self, room_id: str) -> bool:
        """Check if room exists in Redis."""
        return bool(await self.redis.exists(f"room:{room_id}:code"))

    async def get_room_code(self, room_id: str) -> str:
        """Get current code content for room."""
        code = await self.redis.get(f"room:{room_id}:code")
        return code if code else ""

    async def refresh_room_ttl(self, room_id: str) -> None:
        """
        Refresh TTL for all room keys.
        Called on room activity to prevent expiration while users are active.
        """
        ttl = settings.room_ttl_seconds
        await self.redis.expire(f"room:{room_id}:code", ttl)
        await self.redis.expire(f"room:{room_id}:users", ttl)
        await self.redis.expire(f"room:{room_id}:cursors", ttl)
