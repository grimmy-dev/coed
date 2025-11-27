"use client";

import {
  useEffect,
  useRef,
  useState,
  forwardRef,
  useImperativeHandle,
} from "react";
import Editor, { OnMount, OnChange, Monaco } from "@monaco-editor/react";
import type { editor } from "monaco-editor";
import { useAutocomplete } from "@/hooks/use-autocomplete";

interface CodeEditorProps {
  value: string;
  onChange: (value: string) => void;
  onCursorChange: (line: number, column: number) => void;
  language?: string;
  readOnly?: boolean;
}

export interface CodeEditorRef {
  editorRef: React.RefObject<editor.IStandaloneCodeEditor | null>;
}

/**
 * Monaco-based code editor with autocomplete integration
 * Handles local edits and syncs with WebSocket
 */
export const CodeEditor = forwardRef<CodeEditorRef, CodeEditorProps>(
  function CodeEditor(
    { value, onChange, onCursorChange, language = "python", readOnly = false },
    ref
  ) {
    const editorRef = useRef<editor.IStandaloneCodeEditor | null>(null);
    const monacoRef = useRef<Monaco | null>(null);
    const isLocalChangeRef = useRef(false); // Prevent feedback loop
    const [cursorPosition, setCursorPosition] = useState(0);
    const [currentLine, setCurrentLine] = useState(1);
    const [currentColumn, setCurrentColumn] = useState(1);
    const suggestionRef = useRef<string | null>(null);

    useImperativeHandle(ref, () => ({ editorRef }));

    // Get autocomplete suggestions
    const { suggestion } = useAutocomplete(value, cursorPosition, language, {
      enabled: !readOnly,
      debounceMs: 600,
    });

    useEffect(() => {
      suggestionRef.current = suggestion?.suggestion ?? null;
    }, [suggestion]);

    // Initialize editor and set up event handlers
    const handleEditorDidMount: OnMount = (editor, monaco) => {
      editorRef.current = editor;
      monacoRef.current = monaco;

      // Track cursor position for WebSocket broadcast
      editor.onDidChangeCursorPosition((e) => {
        const { lineNumber, column } = e.position;

        onCursorChange(lineNumber, column);
        setCurrentLine(lineNumber);
        setCurrentColumn(column);

        const offset = editor.getModel()?.getOffsetAt(e.position) ?? 0;
        setCursorPosition(offset);
      });

      // Override Tab key to accept autocomplete suggestions
      editor.addCommand(monaco.KeyCode.Tab, () => {
        const suggestionText = suggestionRef.current;

        if (!suggestionText) {
          // Block default tab indentation if no suggestion
          return;
        }

        const model = editor.getModel();
        const position = editor.getPosition();
        if (!model || !position) return;

        // Insert suggestion at cursor
        editor.executeEdits("autocomplete", [
          {
            range: {
              startLineNumber: position.lineNumber,
              startColumn: position.column,
              endLineNumber: position.lineNumber,
              endColumn: position.column,
            },
            text: suggestionText,
          },
        ]);

        // Move cursor to end of inserted text
        const lines = suggestionText.split("\n");
        const lastLine = lines[lines.length - 1];

        editor.setPosition({
          lineNumber: position.lineNumber + (lines.length - 1),
          column:
            lines.length > 1
              ? lastLine.length + 1
              : position.column + lastLine.length,
        });

        // Trigger WebSocket update
        isLocalChangeRef.current = true;
        onChange(editor.getValue());
        setTimeout(() => {
          isLocalChangeRef.current = false;
        }, 50);

        // Clear suggestion after accepting
        suggestionRef.current = null;
      });

      editor.focus();
    };

    // Handle local code changes (user typing)
    const handleEditorChange: OnChange = (newValue) => {
      if (!newValue) return;

      isLocalChangeRef.current = true;
      onChange(newValue);

      setTimeout(() => {
        isLocalChangeRef.current = false;
      }, 50);
    };

    // Sync remote code changes from WebSocket
    useEffect(() => {
      if (!editorRef.current || isLocalChangeRef.current) return;

      const editor = editorRef.current;
      const currentValue = editor.getValue();

      if (currentValue !== value) {
        const pos = editor.getPosition();
        editor.setValue(value);
        if (pos) editor.setPosition(pos); // Preserve cursor
      }
    }, [value]);

    // Show autocomplete suggestion as floating widget
    useEffect(() => {
      if (!editorRef.current || !monacoRef.current || !suggestion) return;

      const editor = editorRef.current;
      const monaco = monacoRef.current;

      const widget: editor.IContentWidget = {
        getId: () => "autocomplete.widget",

        getDomNode: () => {
          const node = document.createElement("div");

          // Style the tooltip container
          node.style.background = "rgba(40, 40, 40, 0.85)";
          node.style.backdropFilter = "blur(6px)";
          node.style.border = "1px solid rgba(255, 255, 255, 0.08)";
          node.style.borderRadius = "8px";
          node.style.padding = "6px 10px";
          node.style.color = "#dcdcdc";
          node.style.fontFamily = "Consolas, monospace";
          node.style.fontSize = "13px";
          node.style.whiteSpace = "pre";
          node.style.boxShadow = "0 6px 18px rgba(0,0,0,0.35)";
          node.style.display = "flex";
          node.style.flexDirection = "column";
          node.style.pointerEvents = "auto";
          node.style.maxWidth = "380px";

          // Preview text (first line of suggestion)
          const previewText = document.createElement("div");
          previewText.textContent = suggestion.suggestion.split("\n")[0];
          previewText.style.color = "#4EC9B0";
          previewText.style.fontWeight = "500";
          previewText.style.marginBottom = "2px";
          previewText.style.overflow = "hidden";
          previewText.style.textOverflow = "ellipsis";
          previewText.style.whiteSpace = "nowrap";

          // Hint text
          const hintText = document.createElement("div");
          hintText.textContent = "Press Tab to accept";
          hintText.style.opacity = "0.6";
          hintText.style.fontSize = "11px";
          hintText.style.marginTop = "0";

          node.appendChild(previewText);
          node.appendChild(hintText);

          return node;
        },

        getPosition: () => ({
          position: { lineNumber: currentLine, column: currentColumn },
          preference: [
            monaco.editor.ContentWidgetPositionPreference.BELOW,
            monaco.editor.ContentWidgetPositionPreference.ABOVE,
          ],
        }),
      };

      editor.addContentWidget(widget);

      return () => {
        editor.removeContentWidget(widget);
      };
    }, [suggestion, currentLine, currentColumn]);

    return (
      <div className="h-full w-full font-mono!">
        <Editor
          height="100%"
          defaultLanguage={language}
          value={value}
          onChange={handleEditorChange}
          onMount={handleEditorDidMount}
          theme="vs-dark"
          options={{
            minimap: { enabled: false },
            fontSize: 14,
            lineNumbers: "on",
            automaticLayout: true,
            roundedSelection: true,
            scrollBeyondLastLine: false,
            tabSize: 2,
            readOnly,
            wordWrap: "on",

            // Disable Monaco's built-in autocomplete (we use custom)
            useTabStops: false,
            tabCompletion: "off",
            quickSuggestions: false,
            suggestOnTriggerCharacters: false,
            snippetSuggestions: "none",
          }}
        />
      </div>
    );
  }
);
