"""
Redis Pub/Sub messaging service.

Manages Redis publish/subscribe channels for real-time message broadcasting
between server instances and WebSocket clients.
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
    Manages Redis Pub/Sub subscriptions for room-based messaging.

    Responsibilities:
        - Subscribe to room channels
        - Listen for Redis messages
        - Forward messages to WebSocket clients
        - Handle channel lifecycle

    This enables horizontal scaling by allowing multiple server instances
    to share room state through Redis pub/sub.
    """

    def __init__(self, redis_client: Redis):
        """
        Initialize pub/sub service with Redis client.

        Args:
            redis_client: Redis client instance for pub/sub operations
        """
        self.redis = redis_client
        self.subscriptions: Dict[str, PubSub] = {}
        self.listener_tasks: Dict[str, asyncio.Task] = {}

    async def subscribe_to_room(self, room_id: str) -> None:
        """
        Subscribe to a room's Redis Pub/Sub channel.

        Creates a channel listener that forwards messages to WebSocket clients.
        If already subscribed, this is a no-op.

        Args:
            room_id: Room to subscribe to
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
        Unsubscribe from a room's channel when no users remain.

        Cancels the listener task and cleans up the PubSub instance.

        Args:
            room_id: Room to unsubscribe from
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
        Listen to messages from a Redis Pub/Sub channel.

        Runs as a background task, continuously listening for messages
        and forwarding them to WebSocket clients in the room.

        Args:
            room_id: Room identifier
            pubsub: Redis PubSub instance to listen on
        """
        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    try:
                        data = json.loads(message["data"])
                        await connection_manager.broadcast_to_room(room_id, data)
                    except json.JSONDecodeError as e:
                        logger.error(f"Failed to parse message: {e}")

        except asyncio.CancelledError:
            logger.info(f"Listener for room {room_id} cancelled")
        except Exception as e:
            logger.error(f"Error in listener for room {room_id}: {e}")

    async def publish_to_room(self, room_id: str, message: dict) -> None:
        """
        Publish a message to a room's channel.

        The message will be received by all server instances subscribed
        to this room and forwarded to their WebSocket clients.

        Args:
            room_id: Room to publish to
            message: Message dictionary to broadcast
        """
        channel_name = f"room_channel:{room_id}"
        message_json = json.dumps(message)

        await self.redis.publish(channel_name, message_json)

        logger.debug(f"Published to {channel_name}: {message.get('type', 'unknown')}")
