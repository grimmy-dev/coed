"""
Code autocomplete service - provides rule-based suggestions.

This is a mocked implementation using pattern matching.
In production, you'd integrate with an AI model or language server.
"""

import re
from typing import Optional


class AutocompleteService:
    """
    Provides code autocomplete suggestions using pattern matching.

    Uses simple rules to detect common patterns and suggest completions.
    Good for demo purposes - replace with real AI model for production.
    """

    def __init__(self):
        """Initialize with suggestion patterns."""
        self._init_patterns()

    def _init_patterns(self) -> None:
        """Initialize pattern-based suggestion rules."""
        # Python keyword patterns
        self.python_patterns = {
            "def ": {"suggestion": "function_name():\n    pass", "trigger": "def"},
            "class ": {
                "suggestion": "ClassName:\n    def __init__(self):\n        pass",
                "trigger": "class",
            },
            "for ": {"suggestion": "item in items:\n    pass", "trigger": "for"},
            "if ": {"suggestion": "condition:\n    pass", "trigger": "if"},
            "while ": {"suggestion": "condition:\n    pass", "trigger": "while"},
            "try": {
                "suggestion": ":\n    pass\nexcept Exception as e:\n    pass",
                "trigger": "try",
            },
            "import ": {"suggestion": "numpy as np", "trigger": "import"},
            "from ": {"suggestion": "module import function", "trigger": "from"},
            "with ": {
                "suggestion": "open('file.txt', 'r') as f:\n    pass",
                "trigger": "with",
            },
            "async def ": {
                "suggestion": "function_name():\n    pass",
                "trigger": "async def",
            },
        }

        # Common import suggestions
        self.common_imports = [
            "import os",
            "import sys",
            "import json",
            "import re",
            "import datetime",
            "import numpy as np",
            "import pandas as pd",
            "from typing import List, Dict, Optional",
        ]

    def get_suggestion(
        self, code: str, cursor_position: int, language: str = "python"
    ) -> Optional[dict]:
        """
        Generate autocomplete suggestion based on code context.

        Args:
            code: Current code content
            cursor_position: Cursor position (0-indexed)
            language: Programming language (only 'python' supported)

        Returns:
            dict with suggestion, insert_position, trigger_word
            None if no suggestion available
        """
        if language != "python":
            return None

        # Get text before cursor
        text_before_cursor = code[:cursor_position]

        # Get current line
        lines = text_before_cursor.split("\n")
        current_line = lines[-1] if lines else ""

        # Check for exact pattern matches
        for pattern, suggestion_data in self.python_patterns.items():
            if current_line.endswith(pattern):
                return {
                    "suggestion": suggestion_data["suggestion"],
                    "insert_position": cursor_position,
                    "trigger_word": suggestion_data["trigger"],
                }

        # Suggest import completion
        if "import" in current_line:
            if current_line.strip() == "import":
                return {
                    "suggestion": " os",
                    "insert_position": cursor_position,
                    "trigger_word": "import",
                }

        # Suggest function parentheses
        if re.search(r"\bdef\s+\w*$", current_line):
            return {
                "suggestion": "():\n    pass",
                "insert_position": cursor_position,
                "trigger_word": "def",
            }

        # Suggest print statement completion
        if current_line.endswith("print"):
            return {
                "suggestion": "()",
                "insert_position": cursor_position,
                "trigger_word": "print",
            }

        # Suggest variable initialization
        if current_line.strip().endswith("="):
            return {
                "suggestion": " None",
                "insert_position": cursor_position,
                "trigger_word": "=",
            }

        return None

    def get_import_suggestions(self, query: str = "") -> list[str]:
        """
        Get list of common import suggestions.
        Can filter by query string.
        """
        if not query:
            return self.common_imports

        # Filter by query
        query_lower = query.lower()
        return [imp for imp in self.common_imports if query_lower in imp.lower()]
