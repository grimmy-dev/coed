/**
 * TypeScript types for the collaborative code editor.
 */

// Cursor position for a user
export interface CursorPosition {
  line: number;
  column: number;
  color: string;
}

// User information
export interface User {
  id: string;
  color: string;
}

// WebSocket connection state
export interface ConnectionState {
  isConnected: boolean;
  error: string | null;
  userId: string | null;
  userColor: string | null;
}

// WebSocket message types
export interface InitMessage {
  type: "init";
  code: string;
  users: string[];
  cursors: Record<string, CursorPosition>;
  your_user_id: string;
  your_color: string;
}

export interface CodeUpdateMessage {
  type: "code_update";
  code: string;
  user_id: string;
}

export interface CursorMoveMessage {
  type: "cursor_move";
  user_id: string;
  line: number;
  column: number;
  color: string;
}

export interface UserJoinedMessage {
  type: "user_joined";
  user_id: string;
  color: string;
}

export interface UserLeftMessage {
  type: "user_left";
  user_id: string;
}

export type WebSocketMessage =
  | InitMessage
  | CodeUpdateMessage
  | CursorMoveMessage
  | UserJoinedMessage
  | UserLeftMessage;
