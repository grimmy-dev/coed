"use client";

import { useState, useCallback, useRef, useEffect } from "react";
import { ApiClient } from "@/lib/api";

interface AutocompleteSuggestion {
  suggestion: string;
  insert_position: number;
  trigger_word?: string;
}

interface UseAutocompleteOptions {
  debounceMs?: number;
  enabled?: boolean;
}

/**
 * Provides debounced autocomplete suggestions from the backend
 * Waits for typing to pause before making API request
 */
export function useAutocomplete(
  code: string,
  cursorPosition: number,
  language: string = "python",
  options: UseAutocompleteOptions = {}
) {
  const { debounceMs = 600, enabled = true } = options;

  const [suggestion, setSuggestion] = useState<AutocompleteSuggestion | null>(
    null
  );
  const [isLoading, setIsLoading] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  // Request suggestion from backend
  const fetchSuggestion = useCallback(async () => {
    if (!enabled) return;

    setIsLoading(true);

    try {
      const result = await ApiClient.getAutocomplete(
        code,
        cursorPosition,
        language
      );
      setSuggestion(result);
    } catch (error) {
      // No suggestion available - this is normal behavior
      setSuggestion(null);
    } finally {
      setIsLoading(false);
    }
  }, [code, cursorPosition, language, enabled]);

  // Debounce autocomplete requests (wait for user to stop typing)
  useEffect(() => {
    if (!enabled) {
      setSuggestion(null);
      return;
    }

    // Clear existing timeout
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Set new timeout
    timeoutRef.current = setTimeout(() => {
      fetchSuggestion();
    }, debounceMs);

    // Cleanup
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [code, cursorPosition, enabled, debounceMs, fetchSuggestion]);

  const clearSuggestion = useCallback(() => {
    setSuggestion(null);
  }, []);

  return {
    suggestion,
    isLoading,
    clearSuggestion,
  };
}
