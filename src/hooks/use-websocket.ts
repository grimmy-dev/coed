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

  // Handle incoming WebSocket messages
  const handleMessage = useCallback((event: MessageEvent) => {
    try {
      const message: WebSocketMessage = JSON.parse(event.data);

      switch (message.type) {
        case "init":
          // Initial state when connecting
          setCode(message.code);
          setConnectionState((prev) => ({
            ...prev,
            userId: message.your_user_id,
            userColor: message.your_color,
          }));

          // Set users
          const usersMap = new Map<string, { id: string; color: string }>();
          message.users.forEach((userId) => {
            usersMap.set(userId, {
              id: userId,
              color:
                userId === message.your_user_id ? message.your_color : "#999",
            });
          });
          setUsers(usersMap);

          // Set cursors
          const cursorsMap = new Map<string, CursorPosition>();
          Object.entries(message.cursors).forEach(([userId, cursor]) => {
            cursorsMap.set(userId, cursor);
          });
          setCursors(cursorsMap);
          break;

        case "code_update":
          // Another user updated code
          setCode(message.code);
          break;

        case "cursor_move":
          // Another user moved cursor
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
          // New user joined room
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
          // User left room
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

  // Connect to WebSocket
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

      // Auto-reconnect after 3 seconds if not normal closure
      if (event.code !== 1000) {
        reconnectTimeoutRef.current = setTimeout(() => {
          // Trigger re-render to reconnect
        }, 3000);
      }
    };

    // Cleanup on unmount
    return () => {
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      if (ws.readyState === WebSocket.OPEN) {
        ws.close(1000, "Component unmounted");
      }
    };
  }, [roomId, handleMessage]);

  // Send code update to server
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

  // Send cursor position to server
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
