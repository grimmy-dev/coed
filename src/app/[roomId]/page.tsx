"use client";

import { useCallback, useMemo, use, useRef, useState, useEffect } from "react";
import { useWebSocket } from "@/hooks/use-websocket";
import {
  CodeEditor,
  type CodeEditorRef,
} from "@/components/editor/code-editor";
import { CursorOverlay } from "@/components/editor/cursor-overlay";
import { UserSidebar } from "@/components/room/user-sidebar";
import { RoomToolbar } from "@/components/room/toolbar";
import { debounce, throttle } from "@/lib/utils";
import { Loader2 } from "lucide-react";

interface RoomPageProps {
  params: Promise<{
    roomId: string;
  }>;
}

export default function RoomPage({ params }: RoomPageProps) {
  const { roomId } = use(params);
  const codeEditorRef = useRef<CodeEditorRef>(null);
  const [editorReady, setEditorReady] = useState(false);

  // WebSocket connection and room state
  const {
    connectionState,
    code,
    cursors,
    users,
    sendCodeUpdate,
    sendCursorMove,
  } = useWebSocket(roomId);

  // Check if editor is ready
  useEffect(() => {
    if (codeEditorRef.current?.editorRef?.current) {
      setEditorReady(true);
    }
  }, [codeEditorRef.current]);

  // Debounce code updates (300ms)
  const debouncedCodeUpdate = useMemo(
    () =>
      debounce((newCode: string) => {
        sendCodeUpdate(newCode);
      }, 300),
    [sendCodeUpdate]
  );

  // Throttle cursor updates (100ms)
  const throttledCursorUpdate = useMemo(
    () =>
      throttle((line: number, column: number) => {
        sendCursorMove(line, column);
      }, 100),
    [sendCursorMove]
  );

  const handleCodeChange = useCallback(
    (newCode: string) => {
      debouncedCodeUpdate(newCode);
    },
    [debouncedCodeUpdate]
  );

  const handleCursorChange = useCallback(
    (line: number, column: number) => {
      throttledCursorUpdate(line, column);
    },
    [throttledCursorUpdate]
  );

  return (
    <div className="h-screen flex flex-col bg-background">
      {/* Toolbar */}
      <RoomToolbar roomId={roomId} connectionState={connectionState} />

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Editor Area */}
        <div className="flex-1 relative">
          {/* Code Editor */}
          <CodeEditor
            ref={codeEditorRef}
            value={code}
            onChange={handleCodeChange}
            onCursorChange={handleCursorChange}
            language="python"
            readOnly={!connectionState.isConnected}
          />

          {/* Cursor Overlay - always render */}
          <CursorOverlay
            cursors={cursors}
            currentUserId={connectionState.userId}
            editorRef={codeEditorRef.current?.editorRef || { current: null }}
          />

          {/* Connection Error Overlay */}
          {connectionState.error && (
            <div className="absolute inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50">
              <div className="bg-destructive/10 border border-destructive rounded-lg p-6 max-w-md mx-4">
                <h3 className="text-destructive font-semibold mb-2">
                  Connection Error
                </h3>
                <p className="text-destructive/80 text-sm mb-3">
                  {connectionState.error}
                </p>
                <p className="text-muted-foreground text-xs">
                  Make sure the backend server is running and the room exists.
                </p>
              </div>
            </div>
          )}

          {/* Connecting Overlay */}
          {!connectionState.isConnected && !connectionState.error && (
            <div className="absolute inset-0 bg-background/60 backdrop-blur-sm flex items-center justify-center z-40">
              <div className="bg-card border border-border rounded-lg p-6 shadow-lg">
                <div className="flex items-center gap-3">
                  <Loader2 className="size-5 text-primary animate-spin" />
                  <span className="text-foreground font-medium">
                    Connecting to room...
                  </span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* User Sidebar */}
        <UserSidebar users={users} currentUserId={connectionState.userId} />
      </div>
    </div>
  );
}
