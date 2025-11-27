const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface CreateRoomResponse {
  room_id: string;
  join_url: string;
  ws_url: string;
}

export interface RoomExistsResponse {
  exists: boolean;
  room_id: string;
}

export interface AutocompleteResponse {
  suggestion: string;
  insert_position: number;
  trigger_word?: string;
}

/**
 * API client for backend communication
 * Handles room management and autocomplete requests
 */
export class ApiClient {
  // Create a new collaborative room
  static async createRoom(): Promise<CreateRoomResponse> {
    const response = await fetch(`${API_URL}/rooms`, {
      method: "POST",
    });

    if (!response.ok) {
      throw new Error("Failed to create room");
    }

    return response.json();
  }

  // Check if room exists before joining
  static async checkRoomExists(roomId: string): Promise<RoomExistsResponse> {
    const response = await fetch(`${API_URL}/rooms/${roomId}/exists`);

    if (!response.ok) {
      throw new Error("Failed to check room");
    }

    return response.json();
  }

  // Get autocomplete suggestion based on current code context
  static async getAutocomplete(
    code: string,
    cursorPosition: number,
    language: string = "python"
  ): Promise<AutocompleteResponse> {
    const response = await fetch(`${API_URL}/rooms/autocomplete`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        code,
        cursor_position: cursorPosition,
        language,
      }),
    });

    if (!response.ok) {
      throw new Error("No autocomplete suggestion available");
    }

    return response.json();
  }
}
