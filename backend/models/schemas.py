"""
Pydantic models for request/response validation and serialization.

Defines all data structures used in API endpoints and WebSocket messages.
"""

from typing import Dict, Literal, Optional

from pydantic import BaseModel, Field


# ============================================================================
# REST API Models
# ============================================================================


class RoomCreateResponse(BaseModel):
    """Response model for room creation endpoint."""

    room_id: str = Field(..., description="Unique room identifier")
    join_url: str = Field(..., description="URL to join the room")
    ws_url: str = Field(..., description="WebSocket connection URL")


class RoomExistsResponse(BaseModel):
    """Response model for room existence check endpoint."""

    exists: bool = Field(..., description="Whether the room exists")
    room_id: str = Field(..., description="Room identifier that was checked")


class AutocompleteRequest(BaseModel):
    """Request model for code autocomplete endpoint."""

    code: str = Field(..., description="Current code content")
    cursor_position: int = Field(..., description="Cursor position in code", ge=0)
    language: str = Field(default="python", description="Programming language")


class AutocompleteResponse(BaseModel):
    """Response model for code autocomplete endpoint."""

    suggestion: str = Field(..., description="Autocomplete suggestion text")
    insert_position: int = Field(..., description="Position to insert suggestion")
    trigger_word: Optional[str] = Field(
        None, description="Word that triggered suggestion"
    )


class ErrorResponse(BaseModel):
    """Standard error response model."""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")


# ============================================================================
# WebSocket Message Models
# ============================================================================


class CursorPosition(BaseModel):
    """Cursor position data for a user."""

    line: int = Field(..., description="Line number (1-indexed)", ge=1)
    column: int = Field(..., description="Column number (0-indexed)", ge=0)
    color: str = Field(default="#FF0000", description="Cursor color hex code")


class InitMessage(BaseModel):
    """Initial state message sent when client connects to room."""

    type: Literal["init"] = "init"
    code: str = Field(..., description="Current code in the room")
    users: list[str] = Field(..., description="List of user IDs in room")
    cursors: Dict[str, CursorPosition] = Field(
        ..., description="Current cursor positions"
    )
    your_user_id: str = Field(..., description="This client's user ID")
    your_color: str = Field(..., description="This client's cursor color")


class CodeUpdateMessage(BaseModel):
    """Code update message from a user."""

    type: Literal["code_update"] = "code_update"
    code: str = Field(..., description="Updated code content")
    user_id: str = Field(..., description="User who made the update")


class CursorMoveMessage(BaseModel):
    """Cursor movement message from a user."""

    type: Literal["cursor_move"] = "cursor_move"
    user_id: str = Field(..., description="User who moved cursor")
    line: int = Field(..., description="New line position", ge=1)
    column: int = Field(..., description="New column position", ge=0)
    color: str = Field(..., description="Cursor color")


class UserJoinedMessage(BaseModel):
    """User joined room message."""

    type: Literal["user_joined"] = "user_joined"
    user_id: str = Field(..., description="ID of user who joined")
    color: str = Field(..., description="User's cursor color")


class UserLeftMessage(BaseModel):
    """User left room message."""

    type: Literal["user_left"] = "user_left"
    user_id: str = Field(..., description="ID of user who left")


class ErrorMessage(BaseModel):
    """Error message for WebSocket clients."""

    type: Literal["error"] = "error"
    message: str = Field(..., description="Error description")
