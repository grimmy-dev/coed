"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { ApiClient } from "@/lib/api";
import { Button } from "@/components/ui/button";
import {
  ArrowRightToLineIcon,
  CheckCircle2Icon,
  Loader2,
  PlusIcon,
} from "lucide-react";

export default function HomePage() {
  const router = useRouter();
  const [joinCode, setJoinCode] = useState("");
  const [isCreating, setIsCreating] = useState(false);
  const [isJoining, setIsJoining] = useState(false);
  const [error, setError] = useState("");

  const handleCreateRoom = async () => {
    setError("");
    setIsCreating(true);

    try {
      const response = await ApiClient.createRoom();
      // Navigate to the created room (FIXED: consistent routing)
      router.push(`/${response.room_id}`);
    } catch (err) {
      setError("Failed to create room. Make sure backend is running.");
      setIsCreating(false);
    }
  };

  const handleJoinRoom = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!joinCode.trim()) {
      setError("Please enter a room code");
      return;
    }

    setError("");
    setIsJoining(true);

    try {
      const response = await ApiClient.checkRoomExists(joinCode.trim());

      if (response.exists) {
        // Navigate to the room (FIXED: removed /room/ prefix for consistency)
        router.push(`/${joinCode.trim()}`);
      } else {
        setError("Room not found. Check the code and try again.");
        setIsJoining(false);
      }
    } catch (err) {
      setError("Failed to check room. Make sure backend is running.");
      setIsJoining(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-md w-full space-y-6">
        {/* Header */}
        <div className="text-center space-y-2">
          <h1 className="text-4xl font-bold">Collaborative Code Editor</h1>
          <p className="text-muted-foreground text-lg">
            Code together in real-time
          </p>
        </div>

        {/* Main Card */}
        <div className="bg-card border rounded-lg shadow-lg p-8 space-y-6">
          {/* Create Room Section */}
          <div>
            <h2 className="text-lg font-medium mb-3">Start a New Session</h2>
            <Button
              size="lg"
              variant="secondary"
              onClick={handleCreateRoom}
              disabled={isCreating}
              className="w-full font-semibold"
            >
              {isCreating ? (
                <>
                  <Loader2 className="size-5 animate-spin mr-2" />
                  Creating...
                </>
              ) : (
                <>
                  <PlusIcon className="size-5 mr-2" />
                  Create New Room
                </>
              )}
            </Button>
          </div>

          {/* Divider */}
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-border" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-card text-muted-foreground font-medium">
                OR
              </span>
            </div>
          </div>

          {/* Join Room Section */}
          <div>
            <h2 className="text-lg font-medium mb-3">Join Existing Session</h2>
            <form onSubmit={handleJoinRoom} className="space-y-3">
              <input
                type="text"
                value={joinCode}
                onChange={(e) => setJoinCode(e.target.value)}
                placeholder="Enter room code (e.g., a972ed)"
                className="w-full bg-input border border-border text-foreground placeholder:text-muted-foreground rounded-lg px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-ring focus:border-transparent transition-shadow"
                disabled={isJoining}
              />
              <Button
                size="lg"
                type="submit"
                disabled={isJoining || !joinCode.trim()}
                className="w-full font-semibold"
              >
                {isJoining ? (
                  <>
                    <Loader2 className="size-5 animate-spin mr-2" />
                    Joining...
                  </>
                ) : (
                  <>
                    Join Room
                    <ArrowRightToLineIcon className="size-5 ml-2" />
                  </>
                )}
              </Button>
            </form>
          </div>

          {/* Error Message */}
          {error && (
            <div className="bg-destructive/10 border border-destructive/50 rounded-lg p-3">
              <p className="text-destructive text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* Features */}
        <div className="flex items-center justify-center gap-6 text-muted-foreground text-sm">
          <div className="flex items-center gap-2">
            <CheckCircle2Icon className="size-4 text-chart-2" />
            <span>Real-time sync</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2Icon className="size-4 text-chart-2" />
            <span>Live cursors</span>
          </div>
          <div className="flex items-center gap-2">
            <CheckCircle2Icon className="size-4 text-chart-2" />
            <span>No sign-up</span>
          </div>
        </div>
      </div>
    </div>
  );
}
