"""
Redis Pub/Sub service for multi-server message broadcasting.

Enables horizontal scaling by allowing multiple server instances
to share room state through Redis pub/sub channels.
"""

import asyncio
import json
import logging
from typing import Dict

from redis.asyncio import Redis
from redis.asyncio.client import PubSub

from .connection_manager import connection_manager

logger = logging.getLogger(__name__)


class PubSubService:
    """
    Manages Redis Pub/Sub for room-based messaging.

    Each room has its own channel: "room_channel:{room_id}"

    When a message is published:
        1. Redis broadcasts to all subscribed servers
        2. Each server forwards to its local WebSocket clients
        3. This enables real-time sync across multiple servers
    """

    def __init__(self, redis_client: Redis):
        """Initialize with Redis client."""
        self.redis = redis_client
        self.subscriptions: Dict[str, PubSub] = {}  # room_id -> PubSub
        self.listener_tasks: Dict[str, asyncio.Task] = {}  # room_id -> Task

    async def subscribe_to_room(self, room_id: str) -> None:
        """
        Subscribe to a room's Redis channel.

        Creates background listener that forwards messages to WebSocket clients.
        If already subscribed, this is a no-op.
        """
        if room_id in self.subscriptions:
            return  # Already subscribed

        channel_name = f"room_channel:{room_id}"

        # Create PubSub instance
        pubsub = self.redis.pubsub()
        await pubsub.subscribe(channel_name)

        self.subscriptions[room_id] = pubsub

        # Start background listener task
        task = asyncio.create_task(self._listen_to_channel(room_id, pubsub))
        self.listener_tasks[room_id] = task

        logger.info(f"Subscribed to channel: {channel_name}")

    async def unsubscribe_from_room(self, room_id: str) -> None:
        """
        Unsubscribe from room channel when no users remain.
        Cancels listener task and cleans up PubSub instance.
        """
        if room_id not in self.subscriptions:
            return

        # Cancel listener task
        if room_id in self.listener_tasks:
            self.listener_tasks[room_id].cancel()
            del self.listener_tasks[room_id]

        # Unsubscribe and cleanup
        pubsub = self.subscriptions[room_id]
        await pubsub.unsubscribe(f"room_channel:{room_id}")
        await pubsub.close()

        del self.subscriptions[room_id]

        logger.info(f"Unsubscribed from room: {room_id}")

    async def _listen_to_channel(self, room_id: str, pubsub: PubSub) -> None:
        """
        Background task that listens to Redis channel.

        Continuously receives messages from Redis and forwards them
        to WebSocket clients in this server instance.
        """
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        # Forward to local WebSocket clients
                        await connection_manager.broadcast_to_room(room_id, data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse message: {e}")

        except asyncio.CancelledError:
            logger.info(f"Listener for room {room_id} cancelled")
        except Exception as e:
            logger.error(f"Error in listener for room {room_id}: {e}")

    async def publish_to_room(self, room_id: str, message: dict) -> None:
        """
        Publish message to room's Redis channel.

        Message will be received by all server instances subscribed
        to this room and forwarded to their WebSocket clients.
        """
        channel_name = f"room_channel:{room_id}"
        message_json = json.dumps(message)

        await self.redis.publish(channel_name, message_json)

        logger.debug(f"Published to {channel_name}: {message.get('type', 'unknown')}")
