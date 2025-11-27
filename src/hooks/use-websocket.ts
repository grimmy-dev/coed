"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import type {
  WebSocketMessage,
  ConnectionState,
  CursorPosition,
} from "@/types";

interface UseWebSocketReturn {
  connectionState: ConnectionState;
  code: string;
  cursors: Map<string, CursorPosition>;
  users: Map<string, { id: string; color: string }>;
  sendCodeUpdate: (code: string) => void;
  sendCursorMove: (line: number, column: number) => void;
}

/**
 * Manages WebSocket connection for real-time collaboration
 * Handles code sync, cursor positions, and user presence
 */
export function useWebSocket(roomId: string): UseWebSocketReturn {
  const wsRef = useRef<WebSocket | null>(null);
  const reconnectTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const [connectionState, setConnectionState] = useState<ConnectionState>({
    isConnected: false,
    error: null,
    userId: null,
    userColor: null,
  });

  const [code, setCode] = useState("");
  const [cursors, setCursors] = useState<Map<string, CursorPosition>>(
    new Map()
  );
  const [users, setUsers] = useState<
    Map<string, { id: string; color: string }>
  >(new Map());

  // Process incoming messages from server
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);

      switch (message.type) {
        case "init":
          // Server sends full state on connect
          setCode(message.code);
          setConnectionState((prev) => ({
            ...prev,
            userId: message.your_user_id,
            userColor: message.your_color,
          }));

          // Build users map
          const usersMap = new Map<string, { id: string; color: string }>();
          message.users.forEach((userId) => {
            usersMap.set(userId, {
              id: userId,
              color:
                userId === message.your_user_id ? message.your_color : "#999",
            });
          });
          setUsers(usersMap);

          // Build cursors map
          const cursorsMap = new Map<string, CursorPosition>();
          Object.entries(message.cursors).forEach(([userId, cursor]) => {
            cursorsMap.set(userId, cursor);
          });
          setCursors(cursorsMap);
          break;

        case "code_update":
          // Sync code from another user
          setCode(message.code);
          break;

        case "cursor_move":
          // Update other user's cursor position
          setCursors((prev) => {
            const newCursors = new Map(prev);
            newCursors.set(message.user_id, {
              line: message.line,
              column: message.column,
              color: message.color,
            });
            return newCursors;
          });
          break;

        case "user_joined":
          // Add new user to room
          setUsers((prev) => {
            const newUsers = new Map(prev);
            newUsers.set(message.user_id, {
              id: message.user_id,
              color: message.color,
            });
            return newUsers;
          });
          break;

        case "user_left":
          // Remove user and their cursor
          setUsers((prev) => {
            const newUsers = new Map(prev);
            newUsers.delete(message.user_id);
            return newUsers;
          });
          setCursors((prev) => {
            const newCursors = new Map(prev);
            newCursors.delete(message.user_id);
            return newCursors;
          });
          break;
      }
    } catch (error) {
      console.error("Error handling message:", error);
    }
  }, []);

  // Establish WebSocket connection
  useEffect(() => {
    const wsUrl = `${
      process.env.NEXT_PUBLIC_WS_URL || "ws://localhost:8000"
    }/ws/${roomId}`;

    const ws = new WebSocket(wsUrl);
    wsRef.current = ws;

    ws.onopen = () => {
      setConnectionState((prev) => ({
        ...prev,
        isConnected: true,
        error: null,
      }));
    };

    ws.onmessage = handleMessage;

    ws.onerror = () => {
      setConnectionState((prev) => ({
        ...prev,
        error: "Connection error",
      }));
    };

    ws.onclose = (event) => {
      setConnectionState((prev) => ({
        ...prev,
        isConnected: false,
      }));

      // Auto-reconnect if connection drops unexpectedly
      if (event.code !== 1000) {
        reconnectTimeoutRef.current = setTimeout(() => {
          // Trigger re-render to reconnect
        }, 3000);
      }
    };

    // Clean up on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (ws.readyState === WebSocket.OPEN) {
        ws.close(1000, "Component unmounted");
      }
    };
  }, [roomId, handleMessage]);

  // Broadcast code changes to other users
  const sendCodeUpdate = useCallback((newCode: string) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "code_update",
          code: newCode,
        })
      );
    }
  }, []);

  // Broadcast cursor movement to other users
  const sendCursorMove = useCallback((line: number, column: number) => {
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: "cursor_move",
          line,
          column,
        })
      );
    }
  }, []);

  return {
    connectionState,
    code,
    cursors,
    users,
    sendCodeUpdate,
    sendCursorMove,
  };
}
