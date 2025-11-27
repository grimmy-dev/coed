"""
WebSocket endpoint for real-time collaboration.

Handles WebSocket connections, user presence, code synchronization,
and cursor position updates through Redis pub/sub.
"""

import json
import logging
import secrets

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect
from redis.asyncio import Redis

from config import get_redis
from services import PubSubService, RoomService, connection_manager

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

router = APIRouter()

# Global PubSub service (lazy initialization)
_pubsub_service: PubSubService | None = None


async def get_pubsub_service(redis: Redis = Depends(get_redis)) -> PubSubService:
    """
    Get or create PubSub service instance.

    Uses lazy initialization to create service only when needed.

    Args:
        redis: Redis client instance (injected)

    Returns:
        PubSubService: Global pub/sub service
    """
    global _pubsub_service
    if _pubsub_service is None:
        _pubsub_service = PubSubService(redis)
    return _pubsub_service


def generate_user_id() -> str:
    """
    Generate a unique user identifier.

    Returns:
        str: 16-character hexadecimal user ID
    """
    return secrets.token_hex(8)


def generate_user_color() -> str:
    """
    Generate a random color for user cursor.

    Returns:
        str: Hex color code
    """
    colors = [
        "#C72626",  # Red
        "#1C978F",  # Teal
        "#1E7D92",  # Blue
        "#B3471D",  # Orange
        "#24B792",  # Green
        "#CBAA27",  # Yellow
        "#9A26CB",  # Purple
        "#278BC1",  # Sky blue
    ]
    return secrets.choice(colors)


@router.websocket("/ws/{room_id}")
async def websocket_endpoint(
    websocket: WebSocket, room_id: str, redis: Redis = Depends(get_redis)
):
    """
    WebSocket endpoint for real-time collaboration.

    Connection Flow:
        1. Validate room exists
        2. Accept connection and assign user ID/color
        3. Subscribe to Redis pub/sub channel
        4. Send initial room state to client
        5. Broadcast user joined to other clients
        6. Listen for client messages
        7. Handle disconnect and cleanup

    Args:
        websocket: WebSocket connection
        room_id: Room identifier from URL path
        redis: Redis client (injected)
    """
    room_service = RoomService(redis)
    pubsub_service = await get_pubsub_service(redis)

    # Generate user credentials
    user_id = generate_user_id()
    user_color = generate_user_color()

    # Validate room exists
    if not await room_service.room_exists(room_id):
        await websocket.close(code=4004, reason="Room not found")
        return

    try:
        # Connect WebSocket
        await connection_manager.connect(websocket, room_id, user_id)

        # Subscribe to room's pub/sub channel
        await pubsub_service.subscribe_to_room(room_id)

        # Add user to Redis users set
        await redis.sadd(f"room:{room_id}:users", user_id)

        # Get current room state
        code = await room_service.get_room_code(room_id)
        users = list(await redis.smembers(f"room:{room_id}:users"))

        # Get cursor positions
        cursors_raw = await redis.hgetall(f"room:{room_id}:cursors")
        cursors = {}
        for uid, cursor_json in cursors_raw.items():
            try:
                cursors[uid] = json.loads(cursor_json)
            except json.JSONDecodeError:
                pass

        # Send initial state to this client
        await websocket.send_json(
            {
                "type": "init",
                "code": code or "",
                "users": users,
                "cursors": cursors,
                "your_user_id": user_id,
                "your_color": user_color,
            }
        )

        # Broadcast user joined to others
        await pubsub_service.publish_to_room(
            room_id, {"type": "user_joined", "user_id": user_id, "color": user_color}
        )

        # Refresh room TTL
        await room_service.refresh_room_ttl(room_id)

        # Listen for client messages
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)

            await handle_client_message(
                message=message,
                room_id=room_id,
                user_id=user_id,
                user_color=user_color,
                redis=redis,
                room_service=room_service,
                pubsub_service=pubsub_service,
            )

    except WebSocketDisconnect:
        logger.info(f"User {user_id} disconnected from room {room_id}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")

    finally:
        # Cleanup on disconnect
        await cleanup_connection(
            websocket=websocket,
            room_id=room_id,
            user_id=user_id,
            redis=redis,
            pubsub_service=pubsub_service,
        )


async def handle_client_message(
    message: dict,
    room_id: str,
    user_id: str,
    user_color: str,
    redis: Redis,
    room_service: RoomService,
    pubsub_service: PubSubService,
) -> None:
    """
    Handle incoming messages from WebSocket client.

    Message Types:
        - code_update: User edited code
        - cursor_move: User moved cursor

    Args:
        message: Parsed JSON message from client
        room_id: Room identifier
        user_id: User who sent the message
        user_color: User's cursor color
        redis: Redis client
        room_service: Room service instance
        pubsub_service: Pub/sub service instance
    """
    msg_type = message.get("type")

    if msg_type == "code_update":
        # Update code in Redis
        code = message.get("code", "")
        await redis.set(f"room:{room_id}:code", code)

        # Publish to other clients
        await pubsub_service.publish_to_room(
            room_id, {"type": "code_update", "code": code, "user_id": user_id}
        )

        # Refresh TTL on activity
        await room_service.refresh_room_ttl(room_id)

    elif msg_type == "cursor_move":
        # Update cursor position in Redis
        cursor_data = {
            "line": message.get("line", 1),
            "column": message.get("column", 0),
            "color": user_color,
        }
        await redis.hset(f"room:{room_id}:cursors", user_id, json.dumps(cursor_data))

        # Publish cursor movement
        await pubsub_service.publish_to_room(
            room_id,
            {
                "type": "cursor_move",
                "user_id": user_id,
                "line": cursor_data["line"],
                "column": cursor_data["column"],
                "color": cursor_data["color"],
            },
        )


async def cleanup_connection(
    websocket: WebSocket,
    room_id: str,
    user_id: str,
    redis: Redis,
    pubsub_service: PubSubService,
) -> None:
    """
    Clean up resources when user disconnects.

    Cleanup Steps:
        1. Remove from connection manager
        2. Remove user from Redis
        3. Remove cursor position
        4. Broadcast user left
        5. Unsubscribe from pub/sub if room empty

    Args:
        websocket: WebSocket connection
        room_id: Room identifier
        user_id: User identifier
        redis: Redis client
        pubsub_service: Pub/sub service instance
    """
    # Remove from connection manager
    connection_manager.disconnect(websocket)

    # Remove user data from Redis
    await redis.srem(f"room:{room_id}:users", user_id)
    await redis.hdel(f"room:{room_id}:cursors", user_id)

    # Broadcast user left
    await pubsub_service.publish_to_room(
        room_id, {"type": "user_left", "user_id": user_id}
    )

    # Unsubscribe if no users left
    if connection_manager.get_connection_count(room_id) == 0:
        await pubsub_service.unsubscribe_from_room(room_id)
        logger.info(f"Room {room_id} is now empty")
