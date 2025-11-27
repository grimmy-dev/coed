"""
Room management REST API endpoints.

Provides HTTP endpoints for creating rooms, checking existence,
and autocomplete functionality.
"""

from fastapi import APIRouter, Depends, HTTPException
from redis.asyncio import Redis

from config import get_redis, settings
from models import (
    AutocompleteRequest,
    AutocompleteResponse,
    RoomCreateResponse,
    RoomExistsResponse,
)
from services import AutocompleteService, RoomService

router = APIRouter()


def get_room_service(redis: Redis = Depends(get_redis)) -> RoomService:
    """
    Dependency injection for RoomService.

    Args:
        redis: Redis client instance (injected)

    Returns:
        RoomService: Initialized room service
    """
    return RoomService(redis)


@router.post("", response_model=RoomCreateResponse, status_code=201)
async def create_room(
    room_service: RoomService = Depends(get_room_service),
) -> RoomCreateResponse:
    """
    Create a new collaborative coding room.

    Generates a unique room ID and initializes the room in Redis.

    Args:
        room_service: Room service instance (injected)

    Returns:
        RoomCreateResponse: Room ID and connection URLs

    Raises:
        HTTPException: If room creation fails
    """
    try:
        room_id, _ = await room_service.create_room()

        return RoomCreateResponse(
            room_id=room_id,
            join_url=f"{settings.base_url}/{room_id}",
            ws_url=f"ws://localhost:8000/ws/{room_id}",
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create room: {str(e)}")


@router.get("/{room_id}/exists", response_model=RoomExistsResponse)
async def check_room_exists(
    room_id: str, room_service: RoomService = Depends(get_room_service)
) -> RoomExistsResponse:
    """
    Check if a room exists.

    Args:
        room_id: Room identifier to check
        room_service: Room service instance (injected)

    Returns:
        RoomExistsResponse: Whether the room exists
    """
    exists = await room_service.room_exists(room_id)
    return RoomExistsResponse(exists=exists, room_id=room_id)


@router.post("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(request: AutocompleteRequest) -> AutocompleteResponse:
    """
    Get code autocomplete suggestions.

    Provides mocked autocomplete based on pattern matching.
    This endpoint demonstrates the autocomplete flow without requiring
    actual AI/ML models.

    Args:
        request: Autocomplete request with code and cursor position

    Returns:
        AutocompleteResponse: Suggested completion

    Raises:
        HTTPException: If no suggestion available
    """
    service = AutocompleteService()

    suggestion = service.get_suggestion(
        code=request.code,
        cursor_position=request.cursor_position,
        language=request.language,
    )

    if suggestion is None:
        raise HTTPException(
            status_code=404,
            detail="No autocomplete suggestion available for current context",
        )

    return AutocompleteResponse(
        suggestion=suggestion["suggestion"],
        insert_position=suggestion["insert_position"],
        trigger_word=suggestion.get("trigger_word"),
    )
