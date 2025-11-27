from typing import Dict, Set
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for collaborative rooms.
    
    Responsibilities:
    - Track active connections per room
    - Broadcast messages to room participants
    - Handle connection lifecycle
    """
    
    def __init__(self):
        # room_id -> set of WebSocket connections
        self.active_connections: Dict[str, Set[WebSocket]] = {}
        # websocket -> (room_id, user_id)
        self.connection_info: Dict[WebSocket, tuple[str, str]] = {}
    
    async def connect(self, websocket: WebSocket, room_id: str, user_id: str):
        """Add a WebSocket connection to a room."""
        await websocket.accept()
        
        # Initialize room set if doesn't exist
        if room_id not in self.active_connections:
            self.active_connections[room_id] = set()
        
        # Add connection
        self.active_connections[room_id].add(websocket)
        self.connection_info[websocket] = (room_id, user_id)
        
        logger.info(f"User {user_id} connected to room {room_id}")
    
    def disconnect(self, websocket: WebSocket):
        """Remove a WebSocket connection."""
        if websocket in self.connection_info:
            room_id, user_id = self.connection_info[websocket]
            
            # Remove from room
            if room_id in self.active_connections:
                self.active_connections[room_id].discard(websocket)
                
                # Clean up empty room
                if not self.active_connections[room_id]:
                    del self.active_connections[room_id]
            
            # Remove connection info
            del self.connection_info[websocket]
            
            logger.info(f"User {user_id} disconnected from room {room_id}")
            
            return room_id, user_id
        
        return None, None
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude: WebSocket = None):
        """
        Broadcast a message to all connections in a room.
        
        Args:
            room_id: The room to broadcast to
            message: The message dict to send
            exclude: Optional WebSocket to exclude from broadcast
        """
        if room_id not in self.active_connections:
            return
        
        # Get list of connections (copy to avoid modification during iteration)
        connections = list(self.active_connections[room_id])
        
        for connection in connections:
            if connection != exclude:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Error sending to connection: {e}")
                    # Connection is dead, remove it
                    self.disconnect(connection)
    
    def get_room_users(self, room_id: str) -> list[str]:
        """Get list of user IDs in a room."""
        if room_id not in self.active_connections:
            return []
        
        user_ids = []
        for ws in self.active_connections[room_id]:
            if ws in self.connection_info:
                _, user_id = self.connection_info[ws]
                user_ids.append(user_id)
        
        return user_ids
    
    def get_connection_count(self, room_id: str) -> int:
        """Get number of active connections in a room."""
        if room_id not in self.active_connections:
            return 0
        return len(self.active_connections[room_id])


# Global connection manager instance
connection_manager = ConnectionManager()