"use client";

import type { ConnectionState } from "@/types";
import { AlertCircleIcon, CircleIcon, Loader2 } from "lucide-react";

interface ConnectionStatusProps {
  connectionState: ConnectionState;
}

export function ConnectionStatus({ connectionState }: ConnectionStatusProps) {
  const { isConnected, error } = connectionState;

  return (
    <div className="flex items-center gap-2 text-sm">
      {isConnected ? (
        <>
          <CircleIcon className="size-2 fill-chart-2 text-chart-2 animate-pulse" />
          <span className="text-chart-2 font-medium">Connected</span>
        </>
      ) : error ? (
        <>
          <AlertCircleIcon className="size-4 text-destructive" />
          <span className="text-destructive font-medium">
            {error || "Connection error"}
          </span>
        </>
      ) : (
        <>
          <Loader2 className="size-4 text-chart-3 animate-spin" />
          <span className="text-chart-3 font-medium">Connecting...</span>
        </>
      )}
    </div>
  );
}
