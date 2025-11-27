"use client";

import { useEffect, useState } from "react";
import type { CursorPosition } from "@/types";
import type { editor } from "monaco-editor";

interface CursorOverlayProps {
  cursors: Map<string, CursorPosition>;
  currentUserId: string | null;
  editorRef: React.RefObject<editor.IStandaloneCodeEditor | null>;
}

interface EditorMeasurements {
  lineHeight: number;
  characterWidth: number;
  contentLeft: number;
}

// Map backend colors to Tailwind-style colors
const COLOR_MAP: Record<string, string> = {
  "#C72626": "#ef4444", // Red
  "#1C978F": "#14b8a6", // Teal
  "#1E7D92": "#0ea5e9", // Blue
  "#B3471D": "#f97316", // Orange
  "#24B792": "#10b981", // Green
  "#CBAA27": "#eab308", // Yellow
  "#9A26CB": "#a855f7", // Purple
  "#278BC1": "#3b82f6", // Sky blue
};

const mapToColor = (hexColor: string): string => {
  return COLOR_MAP[hexColor] || "#6366f1"; // Default indigo
};

/**
 * Displays other users' cursors overlaid on the Monaco editor
 * Calculates positions based on Monaco's actual measurements
 */
export function CursorOverlay({
  cursors,
  currentUserId,
  editorRef,
}: CursorOverlayProps) {
  const [measurements, setMeasurements] = useState<EditorMeasurements>({
    lineHeight: 19,
    characterWidth: 8.4,
    contentLeft: 70,
  });

  // Get Monaco's actual line height and character width
  useEffect(() => {
    if (!editorRef.current) return;

    const editor = editorRef.current;

    const updateMeasurements = () => {
      try {
        // Get Monaco layout info
        const layoutInfo = editor.getLayoutInfo();

        // Get editor options
        const options = editor.getOptions();
        const lineHeightOption = options.get(60); // lineHeight option ID
        const fontSizeOption = options.get(51); // fontSize option ID

        // Extract numeric values
        const lineHeight =
          typeof lineHeightOption === "number" ? lineHeightOption : 19;
        const fontSize =
          typeof fontSizeOption === "number" ? fontSizeOption : 14;

        // Calculate character width (monospace approximation)
        const characterWidth = fontSize * 0.6;

        setMeasurements({
          lineHeight,
          characterWidth,
          contentLeft: layoutInfo.contentLeft,
        });

        console.log("📏 Cursor overlay measurements:", {
          lineHeight,
          fontSize,
          characterWidth,
          contentLeft: layoutInfo.contentLeft,
        });
      } catch (error) {
        console.error("Failed to get editor measurements:", error);
      }
    };

    // Initial measurements
    updateMeasurements();

    // Update when layout changes (e.g., window resize)
    const disposable = editor.onDidLayoutChange(() => {
      updateMeasurements();
    });

    return () => {
      disposable.dispose();
    };
  }, [editorRef]);

  // Filter out current user's cursor (don't show own cursor)
  const otherCursors = Array.from(cursors.entries()).filter(
    ([userId]) => userId !== currentUserId
  );

  // Debug logging
  useEffect(() => {
    if (otherCursors.length > 0) {
      console.log("👁️ Rendering cursors:", {
        count: otherCursors.length,
        cursors: otherCursors.map(([id, cursor]) => ({
          id: id.slice(0, 8),
          line: cursor.line,
          column: cursor.column,
          color: cursor.color,
          mappedColor: mapToColor(cursor.color),
        })),
      });
    }
  }, [otherCursors.length]);

  if (otherCursors.length === 0) {
    return null;
  }

  return (
    <div className="absolute inset-0 pointer-events-none z-50">
      {otherCursors.map(([userId, cursor]) => {
        const color = mapToColor(cursor.color);

        // Calculate pixel position from line/column
        const top = (cursor.line - 0.5) * measurements.lineHeight;
        const left =
          measurements.contentLeft +
          (cursor.column - 1) * measurements.characterWidth;

        return (
          <div
            key={userId}
            className="absolute transition-all duration-100 ease-out"
            style={{
              top: `${top}px`,
              left: `${left}px`,
            }}
          >
            {/* Blinking cursor line */}
            <div
              className="w-0.5 animate-pulse"
              style={{
                height: `${measurements.lineHeight}px`,
                backgroundColor: color,
                boxShadow: `0 0 4px ${color}, 0 0 8px ${color}`,
              }}
            />

            {/* User label tooltip */}
            <div
              className="absolute -top-6 left-0 px-2 py-1 rounded text-xs font-medium whitespace-nowrap shadow-lg"
              style={{
                backgroundColor: color,
                color: "#ffffff",
              }}
            >
              {userId.slice(0, 8)}
            </div>
          </div>
        );
      })}
    </div>
  );
}
