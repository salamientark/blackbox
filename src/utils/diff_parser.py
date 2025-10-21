"""
Diff parser utility for parsing Git diffs.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class DiffParser:
    """Parses Git diff patches to extract changed lines."""

    def __init__(self):
        """Initialize diff parser."""
        pass

    def parse_patch(self, patch: str) -> List[Dict[str, int]]:
        """
        Parse a Git diff patch to extract changed line numbers.

        Args:
            patch: Git diff patch string

        Returns:
            List of dictionaries with 'line' and 'type' keys
        """
        if not patch:
            return []

        changed_lines = []
        lines = patch.split("\n")

        current_line = 0

        for line in lines:
            if line.startswith("@@"):
                # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
                match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
                if match:
                    current_line = (
                        int(match.group(1)) - 1
                    )  # -1 because we'll increment before use

            elif line.startswith("+") and not line.startswith("+++"):
                # Added line
                current_line += 1
                changed_lines.append({"line": current_line, "type": "addition"})

            elif line.startswith("-") and not line.startswith("---"):
                # Removed line (don't increment line number)
                changed_lines.append({"line": current_line + 1, "type": "deletion"})

            elif line.startswith(" "):
                # Context line
                current_line += 1

        return changed_lines

    def extract_changed_functions(
        self, patch: str, language: str = "python"
    ) -> List[Dict[str, Any]]:
        """
        Extract information about changed functions/methods.

        Args:
            patch: Git diff patch
            language: Programming language

        Returns:
            List of changed function information
        """
        if not patch:
            return []

        functions = []
        lines = patch.split("\n")

        # Language-specific function patterns
        patterns = {
            "python": r"^\+\s*def\s+(\w+)\s*\(",
            "javascript": r"^\+\s*(?:function\s+(\w+)|(\w+)\s*\([^)]*\)\s*{)",
            "java": r"^\+\s*(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(",
            "go": r"^\+\s*func\s+(\w+)\s*\(",
        }

        pattern = patterns.get(language, patterns["python"])

        for line in lines:
            if line.startswith("+"):
                match = re.search(pattern, line)
                if match:
                    func_name = match.group(1) or match.group(2)
                    if func_name:
                        functions.append(
                            {
                                "name": func_name,
                                "line": len(
                                    [
                                        l
                                        for l in lines[: lines.index(line)]
                                        if not l.startswith("-")
                                    ]
                                ),
                                "type": "function",
                            }
                        )

        return functions

    def get_diff_stats(self, patch: str) -> Dict[str, int]:
        """
        Get statistics from a diff patch.

        Args:
            patch: Git diff patch

        Returns:
            Dictionary with diff statistics
        """
        if not patch:
            return {"additions": 0, "deletions": 0, "changes": 0}

        additions = 0
        deletions = 0

        lines = patch.split("\n")

        for line in lines:
            if line.startswith("+") and not line.startswith("+++"):
                additions += 1
            elif line.startswith("-") and not line.startswith("---"):
                deletions += 1

        return {
            "additions": additions,
            "deletions": deletions,
            "changes": additions + deletions,
        }

    def extract_code_snippets(
        self, patch: str, context_lines: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Extract code snippets with context from diff.

        Args:
            patch: Git diff patch
            context_lines: Number of context lines around changes

        Returns:
            List of code snippets with context
        """
        if not patch:
            return []

        snippets = []
        lines = patch.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]

            if line.startswith("@@"):
                # Parse hunk header
                match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
                if match:
                    start_line = int(match.group(1))

                    # Collect context and changed lines
                    snippet_lines = []
                    changed_start = None

                    j = i + 1
                    current_line = start_line

                    while j < len(lines) and not lines[j].startswith("@@"):
                        line_content = lines[j]

                        if line_content.startswith("+") and not line_content.startswith(
                            "+++"
                        ):
                            if changed_start is None:
                                changed_start = current_line
                            snippet_lines.append(
                                {
                                    "line": current_line,
                                    "content": line_content[1:],  # Remove + prefix
                                    "type": "addition",
                                }
                            )
                            current_line += 1

                        elif line_content.startswith(
                            "-"
                        ) and not line_content.startswith("---"):
                            if changed_start is None:
                                changed_start = current_line
                            snippet_lines.append(
                                {
                                    "line": current_line,
                                    "content": line_content[1:],  # Remove - prefix
                                    "type": "deletion",
                                }
                            )

                        elif line_content.startswith(" "):
                            snippet_lines.append(
                                {
                                    "line": current_line,
                                    "content": line_content[1:],  # Remove space prefix
                                    "type": "context",
                                }
                            )
                            current_line += 1

                        j += 1

                    if snippet_lines:
                        snippets.append(
                            {
                                "start_line": changed_start or start_line,
                                "lines": snippet_lines,
                                "content": "\n".join(
                                    line["content"] for line in snippet_lines
                                ),
                            }
                        )

                    i = j - 1

            i += 1

        return snippets

    def is_significant_change(self, patch: str) -> bool:
        """
        Determine if the diff represents significant changes.

        Args:
            patch: Git diff patch

        Returns:
            True if changes are significant
        """
        if not patch:
            return False

        stats = self.get_diff_stats(patch)

        # Consider significant if:
        # - More than 50 lines changed, OR
        # - More than 10 additions/deletions, OR
        # - Contains function definitions
        if stats["changes"] > 50:
            return True

        if stats["additions"] > 10 or stats["deletions"] > 10:
            return True

        # Check for function changes
        functions = self.extract_changed_functions(patch)
        if functions:
            return True

        return False

    def get_change_complexity(self, patch: str) -> str:
        """
        Assess the complexity of changes in the diff.

        Args:
            patch: Git diff patch

        Returns:
            Complexity level: 'low', 'medium', 'high'
        """
        if not patch:
            return "low"

        stats = self.get_diff_stats(patch)
        functions = self.extract_changed_functions(patch)

        score = 0

        # Size factors
        score += min(stats["changes"] / 10, 5)  # Max 5 points for size
        score += len(functions) * 2  # 2 points per function

        # Type factors
        if stats["deletions"] > stats["additions"] * 2:
            score += 2  # Major refactoring

        if score < 3:
            return "low"
        elif score < 7:
            return "medium"
        else:
            return "high"
