"""
REST API endpoints for room management and autocomplete.
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
    """Dependency injection for RoomService."""
    return RoomService(redis)


@router.post("", response_model=RoomCreateResponse, status_code=201)
async def create_room(
    room_service: RoomService = Depends(get_room_service),
) -> RoomCreateResponse:
    """
    Create a new collaborative coding room.

    Generates unique room ID and initializes in Redis.
    Returns room ID and URLs for joining.
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
    Used by frontend before attempting to join.
    """
    exists = await room_service.room_exists(room_id)
    return RoomExistsResponse(exists=exists, room_id=room_id)


@router.post("/autocomplete", response_model=AutocompleteResponse)
async def autocomplete(request: AutocompleteRequest) -> AutocompleteResponse:
    """
    Get code autocomplete suggestions.

    Uses rule-based pattern matching (mocked implementation).
    In production, this would call an AI model.
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
