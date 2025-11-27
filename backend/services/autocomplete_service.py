"""
Code autocomplete service.

Provides mocked autocomplete suggestions based on simple pattern matching.
This is a simplified implementation that demonstrates the concept without
requiring actual AI/ML models.
"""

import re
from typing import Optional


class AutocompleteService:
    """
    Service for providing code autocomplete suggestions.

    Uses rule-based pattern matching to suggest common code patterns
    based on the current context. This is a mocked implementation suitable
    for demonstration purposes.
    """

    def __init__(self):
        """Initialize autocomplete service with suggestion patterns."""
        self._init_patterns()

    def _init_patterns(self) -> None:
        """Initialize pattern-based suggestion rules."""
        # Python-specific suggestions
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

        # Common Python imports
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
            cursor_position: Cursor position in code (0-indexed)
            language: Programming language (currently only 'python' supported)

        Returns:
            dict: Suggestion with fields:
                - suggestion: The suggested code
                - insert_position: Where to insert the suggestion
                - trigger_word: Word that triggered the suggestion
            Returns None if no suggestion available
        """
        if language != "python":
            return None

        # Get text before cursor
        text_before_cursor = code[:cursor_position]

        # Get current line
        lines = text_before_cursor.split("\n")
        current_line = lines[-1] if lines else ""

        # Check for pattern matches
        for pattern, suggestion_data in self.python_patterns.items():
            if current_line.endswith(pattern):
                return {
                    "suggestion": suggestion_data["suggestion"],
                    "insert_position": cursor_position,
                    "trigger_word": suggestion_data["trigger"],
                }

        # Check for import statement context
        if "import" in current_line:
            # Suggest common import if line is incomplete
            if current_line.strip() == "import":
                return {
                    "suggestion": " os",
                    "insert_position": cursor_position,
                    "trigger_word": "import",
                }

        # Check for function definition patterns
        if re.search(r"\bdef\s+\w*$", current_line):
            return {
                "suggestion": "():\n    pass",
                "insert_position": cursor_position,
                "trigger_word": "def",
            }

        # Check for print statement
        if current_line.endswith("print"):
            return {
                "suggestion": "()",
                "insert_position": cursor_position,
                "trigger_word": "print",
            }

        # Check for common variable patterns
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

        Args:
            query: Optional search query to filter imports

        Returns:
            list: List of import statement suggestions
        """
        if not query:
            return self.common_imports

        # Filter by query
        query_lower = query.lower()
        return [imp for imp in self.common_imports if query_lower in imp.lower()]
