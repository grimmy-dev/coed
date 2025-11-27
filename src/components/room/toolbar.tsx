"use client";

import { useState } from "react";
import type { ConnectionState } from "@/types";
import { ConnectionStatus } from "./connection-status";
import { Button } from "@/components/ui/button";
import { CheckIcon, CopyIcon, LogOutIcon, Share2Icon } from "lucide-react";
import { useRouter } from "next/navigation";

interface RoomToolbarProps {
  roomId: string;
  connectionState: ConnectionState;
}

/**
 * Top toolbar showing room info and actions
 * Features: room code display, share link, leave room
 */
export function RoomToolbar({ roomId, connectionState }: RoomToolbarProps) {
  const [copied, setCopied] = useState(false);
  const router = useRouter();

  // Copy just the room code
  const copyRoomId = () => {
    navigator.clipboard.writeText(roomId);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  // Copy full URL for sharing
  const copyRoomUrl = () => {
    const url = `${process.env.NEXT_PUBLIC_URL}/${roomId}`;
    navigator.clipboard.writeText(url);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="h-14 border-b border-border bg-card px-6 flex items-center justify-between">
      {/* Left: Room info and status */}
      <div className="flex items-center gap-6">
        <div className="flex items-center gap-3">
          <span className="text-muted-foreground text-sm font-medium">
            Room:
          </span>
          <code className="px-2.5 py-1 bg-muted border border-border rounded-md text-xs font-mono text-primary">
            {roomId}
          </code>
          <Button
            title="Copy Room Code"
            size="icon"
            variant="ghost"
            onClick={copyRoomId}
            className="h-8 w-8"
          >
            {copied ? (
              <CheckIcon className="size-4 text-chart-2" />
            ) : (
              <CopyIcon className="size-4" />
            )}
          </Button>
        </div>

        <ConnectionStatus connectionState={connectionState} />
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-3">
        <Button size="sm" onClick={copyRoomUrl} variant="secondary">
          <Share2Icon className="size-4 mr-2" />
          Share Link
        </Button>
        <Button
          variant="destructive"
          size="icon"
          onClick={() => router.replace("/")}
          className="h-8 w-8"
        >
          <LogOutIcon className="size-4" />
        </Button>
      </div>
    </div>
  );
}
