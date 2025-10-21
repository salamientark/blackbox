"""
Bug detection analyzer using pattern matching and heuristics.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class BugDetector:
    """Detects common bug patterns in code."""

    def __init__(self):
        """Initialize bug detector with pattern rules."""
        self.patterns = self._load_patterns()

    def _load_patterns(self) -> List[Dict[str, Any]]:
        """Load bug detection patterns."""
        return [
            # Python patterns
            {
                "pattern": r"except\s*:",
                "language": "python",
                "message": "Bare except clause catches all exceptions, including system exits",
                "severity": "medium",
                "suggestion": "Use specific exception types: except ValueError:",
                "type": "bug",
            },
            {
                "pattern": r"==\s*None|None\s*==",
                "language": "python",
                "message": 'Use "is None" instead of "== None" for None comparisons',
                "severity": "low",
                "suggestion": "Replace with: if variable is None:",
                "type": "quality",
            },
            {
                "pattern": r"\.append\([^)]*\)\s*\.append\(",
                "language": "python",
                "message": "Chaining append() calls - append() returns None",
                "severity": "high",
                "suggestion": "Call append() on separate lines",
                "type": "bug",
            },
            {
                "pattern": r"def\s+\w+\([^)]*\)\s*:\s*pass\s*$",
                "language": "python",
                "message": "Empty function definition",
                "severity": "info",
                "suggestion": 'Add implementation or use "raise NotImplementedError()"',
                "type": "quality",
            },
            # JavaScript/TypeScript patterns
            {
                "pattern": r"==(?!=)",
                "language": "javascript",
                "message": "Use === instead of == for strict equality",
                "severity": "medium",
                "suggestion": "Replace == with ===",
                "type": "bug",
            },
            {
                "pattern": r"!=(?!=)",
                "language": "javascript",
                "message": "Use !== instead of != for strict inequality",
                "severity": "medium",
                "suggestion": "Replace != with !==",
                "type": "bug",
            },
            {
                "pattern": r"var\s+\w+",
                "language": "javascript",
                "message": "Use let or const instead of var",
                "severity": "low",
                "suggestion": "Replace var with let or const",
                "type": "quality",
            },
            {
                "pattern": r"console\.log\(",
                "language": "javascript",
                "message": "Console.log statement found - should be removed in production",
                "severity": "info",
                "suggestion": "Remove or replace with proper logging",
                "type": "quality",
            },
            # Common patterns across languages
            {
                "pattern": r"TODO|FIXME|XXX|HACK",
                "language": "all",
                "message": "TODO/FIXME comment found",
                "severity": "info",
                "suggestion": "Address the TODO or create a tracking issue",
                "type": "quality",
            },
            {
                "pattern": r"debugger;",
                "language": "javascript",
                "message": "Debugger statement found",
                "severity": "high",
                "suggestion": "Remove debugger statement before committing",
                "type": "bug",
            },
            {
                "pattern": r"import\s+pdb|pdb\.set_trace\(\)",
                "language": "python",
                "message": "Debugger import/call found",
                "severity": "high",
                "suggestion": "Remove pdb debugging code before committing",
                "type": "bug",
            },
            # Null/undefined checks
            {
                "pattern": r"\.length\s*(?:>|<|>=|<=|==|===)\s*0",
                "language": "javascript",
                "message": "Potential null/undefined access on .length",
                "severity": "medium",
                "suggestion": "Check if object exists before accessing .length",
                "type": "bug",
            },
            {
                "pattern": r"\w+\.\w+\s*(?:&&|\|\|)",
                "language": "javascript",
                "message": "Potential null/undefined property access",
                "severity": "low",
                "suggestion": "Use optional chaining (?.) or null checks",
                "type": "bug",
            },
            # Resource leaks
            {
                "pattern": r"open\([^)]+\)(?!.*\.close\(\))",
                "language": "python",
                "message": "File opened but not explicitly closed",
                "severity": "medium",
                "suggestion": 'Use "with open(...) as f:" context manager',
                "type": "bug",
            },
            # Infinite loops
            {
                "pattern": r"while\s+True\s*:(?!.*break)",
                "language": "python",
                "message": "Potential infinite loop without break statement",
                "severity": "medium",
                "suggestion": "Add break condition or use for loop with range",
                "type": "bug",
            },
            {
                "pattern": r"while\s*\(\s*true\s*\)(?!.*break)",
                "language": "javascript",
                "message": "Potential infinite loop without break statement",
                "severity": "medium",
                "suggestion": "Add break condition or use for loop",
                "type": "bug",
            },
            # Type issues
            {
                "pattern": r'\+\s*["\']|["\']\s*\+',
                "language": "javascript",
                "message": "String concatenation with + operator",
                "severity": "info",
                "suggestion": "Consider using template literals (`${var}`)",
                "type": "quality",
            },
            # Async/await issues
            {
                "pattern": r"async\s+\w+[^{]*{(?!.*await)",
                "language": "javascript",
                "message": "Async function without await",
                "severity": "low",
                "suggestion": "Remove async keyword if not using await",
                "type": "quality",
            },
            # Array/List issues
            {
                "pattern": r"\.sort\(\)(?!\s*\.reverse)",
                "language": "javascript",
                "message": "Array.sort() modifies array in-place",
                "severity": "info",
                "suggestion": "Consider using [...array].sort() to avoid mutation",
                "type": "quality",
            },
        ]

    def analyze(self, code: str, filename: str) -> List[Dict[str, Any]]:
        """
        Analyze code for bug patterns.

        Args:
            code: Source code to analyze
            filename: Name of the file

        Returns:
            List of detected issues
        """
        issues = []
        language = self._detect_language(filename)

        lines = code.split("\n")

        for pattern_rule in self.patterns:
            # Check if pattern applies to this language
            if pattern_rule["language"] not in ["all", language]:
                continue

            pattern = pattern_rule["pattern"]

            try:
                # Search for pattern in each line
                for line_num, line in enumerate(lines, start=1):
                    matches = re.finditer(pattern, line, re.IGNORECASE)

                    for match in matches:
                        # Skip if in comment (basic check)
                        if self._is_in_comment(line, match.start(), language):
                            continue

                        issues.append(
                            {
                                "type": pattern_rule["type"],
                                "severity": pattern_rule["severity"],
                                "line": line_num,
                                "column": match.start(),
                                "message": pattern_rule["message"],
                                "suggestion": pattern_rule["suggestion"],
                                "code_snippet": line.strip(),
                                "matched_text": match.group(),
                            }
                        )

            except re.error as e:
                logger.error(f"Regex error in pattern {pattern}: {e}")
                continue

        logger.info(f"Bug detector found {len(issues)} issues in {filename}")
        return issues

    def _detect_language(self, filename: str) -> str:
        """Detect programming language from filename."""
        extension_map = {
            ".py": "python",
            ".js": "javascript",
            ".ts": "javascript",
            ".jsx": "javascript",
            ".tsx": "javascript",
            ".java": "java",
            ".go": "go",
            ".rb": "ruby",
            ".php": "php",
            ".c": "c",
            ".cpp": "cpp",
            ".cs": "csharp",
            ".rs": "rust",
            ".swift": "swift",
            ".kt": "kotlin",
        }

        for ext, lang in extension_map.items():
            if filename.endswith(ext):
                return lang

        return "unknown"

    def _is_in_comment(self, line: str, position: int, language: str) -> bool:
        """Check if position is within a comment."""
        # Basic comment detection
        comment_markers = {
            "python": ["#"],
            "javascript": ["//", "/*"],
            "java": ["//", "/*"],
            "go": ["//", "/*"],
            "c": ["//", "/*"],
            "cpp": ["//", "/*"],
        }

        markers = comment_markers.get(language, [])

        for marker in markers:
            comment_pos = line.find(marker)
            if comment_pos != -1 and comment_pos < position:
                return True

        return False

    def check_complexity(self, code: str) -> Dict[str, Any]:
        """
        Check code complexity metrics.

        Args:
            code: Source code

        Returns:
            Complexity metrics
        """
        lines = code.split("\n")

        # Count various metrics
        total_lines = len(lines)
        code_lines = len(
            [l for l in lines if l.strip() and not l.strip().startswith("#")]
        )

        # Count nesting depth
        max_nesting = 0
        current_nesting = 0

        for line in lines:
            stripped = line.lstrip()
            indent = len(line) - len(stripped)

            if stripped.startswith(
                ("if", "for", "while", "def", "class", "try", "with")
            ):
                current_nesting = indent // 4 + 1
                max_nesting = max(max_nesting, current_nesting)

        return {
            "total_lines": total_lines,
            "code_lines": code_lines,
            "max_nesting_depth": max_nesting,
            "complexity_score": code_lines + (max_nesting * 10),
        }
