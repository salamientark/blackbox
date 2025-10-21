"""
Documentation linker - suggests relevant documentation for code patterns.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class DocLinker:
    """Links code patterns to relevant documentation."""

    def __init__(self):
        """Initialize documentation linker with pattern mappings."""
        self.doc_mappings = self._load_doc_mappings()

    def _load_doc_mappings(self) -> List[Dict[str, Any]]:
        """Load documentation link mappings."""
        return [
            # Python Standard Library
            {
                "pattern": r"import\s+requests",
                "language": "python",
                "docs": [
                    {
                        "title": "Requests Documentation",
                        "url": "https://requests.readthedocs.io/",
                        "description": "HTTP library for Python",
                    }
                ],
            },
            {
                "pattern": r"import\s+pandas",
                "language": "python",
                "docs": [
                    {
                        "title": "Pandas Documentation",
                        "url": "https://pandas.pydata.org/docs/",
                        "description": "Data analysis library",
                    }
                ],
            },
            {
                "pattern": r"import\s+numpy",
                "language": "python",
                "docs": [
                    {
                        "title": "NumPy Documentation",
                        "url": "https://numpy.org/doc/",
                        "description": "Numerical computing library",
                    }
                ],
            },
            {
                "pattern": r"from\s+flask\s+import",
                "language": "python",
                "docs": [
                    {
                        "title": "Flask Documentation",
                        "url": "https://flask.palletsprojects.com/",
                        "description": "Web framework for Python",
                    }
                ],
            },
            {
                "pattern": r"from\s+django",
                "language": "python",
                "docs": [
                    {
                        "title": "Django Documentation",
                        "url": "https://docs.djangoproject.com/",
                        "description": "High-level Python web framework",
                    }
                ],
            },
            # JavaScript/Node.js
            {
                "pattern": r'import.*from\s+["\']react["\']',
                "language": "javascript",
                "docs": [
                    {
                        "title": "React Documentation",
                        "url": "https://react.dev/",
                        "description": "JavaScript library for building UIs",
                    }
                ],
            },
            {
                "pattern": r'import.*from\s+["\']express["\']',
                "language": "javascript",
                "docs": [
                    {
                        "title": "Express.js Documentation",
                        "url": "https://expressjs.com/",
                        "description": "Web framework for Node.js",
                    }
                ],
            },
            {
                "pattern": r'import.*from\s+["\']vue["\']',
                "language": "javascript",
                "docs": [
                    {
                        "title": "Vue.js Documentation",
                        "url": "https://vuejs.org/",
                        "description": "Progressive JavaScript framework",
                    }
                ],
            },
            {
                "pattern": r'import.*from\s+["\']axios["\']',
                "language": "javascript",
                "docs": [
                    {
                        "title": "Axios Documentation",
                        "url": "https://axios-http.com/",
                        "description": "Promise-based HTTP client",
                    }
                ],
            },
            # Common patterns and best practices
            {
                "pattern": r"async\s+def|async\s+function",
                "language": "all",
                "docs": [
                    {
                        "title": "Async/Await Guide",
                        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Statements/async_function",
                        "description": "Understanding asynchronous programming",
                    }
                ],
            },
            {
                "pattern": r"try\s*:.*except",
                "language": "python",
                "docs": [
                    {
                        "title": "Python Exception Handling",
                        "url": "https://docs.python.org/3/tutorial/errors.html",
                        "description": "Handling exceptions in Python",
                    }
                ],
            },
            {
                "pattern": r"class\s+\w+.*:",
                "language": "python",
                "docs": [
                    {
                        "title": "Python Classes",
                        "url": "https://docs.python.org/3/tutorial/classes.html",
                        "description": "Object-oriented programming in Python",
                    }
                ],
            },
            {
                "pattern": r"@\w+\s*\n\s*def",
                "language": "python",
                "docs": [
                    {
                        "title": "Python Decorators",
                        "url": "https://realpython.com/primer-on-python-decorators/",
                        "description": "Understanding Python decorators",
                    }
                ],
            },
            {
                "pattern": r"Promise\.",
                "language": "javascript",
                "docs": [
                    {
                        "title": "JavaScript Promises",
                        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/Promise",
                        "description": "Working with Promises",
                    }
                ],
            },
            # Security-related
            {
                "pattern": r"bcrypt|argon2|scrypt",
                "language": "all",
                "docs": [
                    {
                        "title": "Password Hashing Best Practices",
                        "url": "https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html",
                        "description": "OWASP password storage guidelines",
                    }
                ],
            },
            {
                "pattern": r"jwt|jsonwebtoken",
                "language": "all",
                "docs": [
                    {
                        "title": "JWT Best Practices",
                        "url": "https://tools.ietf.org/html/rfc7519",
                        "description": "JSON Web Token specification",
                    }
                ],
            },
            # Database
            {
                "pattern": r"import\s+sqlite3",
                "language": "python",
                "docs": [
                    {
                        "title": "SQLite3 Documentation",
                        "url": "https://docs.python.org/3/library/sqlite3.html",
                        "description": "SQLite database interface",
                    }
                ],
            },
            {
                "pattern": r"from\s+sqlalchemy",
                "language": "python",
                "docs": [
                    {
                        "title": "SQLAlchemy Documentation",
                        "url": "https://docs.sqlalchemy.org/",
                        "description": "Python SQL toolkit and ORM",
                    }
                ],
            },
            {
                "pattern": r"import.*mongoose",
                "language": "javascript",
                "docs": [
                    {
                        "title": "Mongoose Documentation",
                        "url": "https://mongoosejs.com/",
                        "description": "MongoDB object modeling for Node.js",
                    }
                ],
            },
            # Testing
            {
                "pattern": r"import\s+pytest",
                "language": "python",
                "docs": [
                    {
                        "title": "Pytest Documentation",
                        "url": "https://docs.pytest.org/",
                        "description": "Python testing framework",
                    }
                ],
            },
            {
                "pattern": r"import.*jest",
                "language": "javascript",
                "docs": [
                    {
                        "title": "Jest Documentation",
                        "url": "https://jestjs.io/",
                        "description": "JavaScript testing framework",
                    }
                ],
            },
        ]

    def find_relevant_docs(
        self, code_or_message: str, filename: str = ""
    ) -> List[Dict[str, str]]:
        """
        Find relevant documentation links for code or error message.

        Args:
            code_or_message: Code snippet or error message
            filename: Optional filename for language detection

        Returns:
            List of relevant documentation links
        """
        docs = []
        language = self._detect_language(filename) if filename else "all"

        for mapping in self.doc_mappings:
            # Check if mapping applies to this language
            if mapping["language"] not in ["all", language]:
                continue

            pattern = mapping["pattern"]

            try:
                if re.search(pattern, code_or_message, re.IGNORECASE | re.MULTILINE):
                    docs.extend(mapping["docs"])
            except re.error as e:
                logger.error(f"Regex error in pattern {pattern}: {e}")
                continue

        # Remove duplicates
        seen = set()
        unique_docs = []
        for doc in docs:
            doc_id = doc["url"]
            if doc_id not in seen:
                seen.add(doc_id)
                unique_docs.append(doc)

        return unique_docs

    def suggest_docs_for_issue(
        self, issue_type: str, message: str
    ) -> List[Dict[str, str]]:
        """
        Suggest documentation based on issue type and message.

        Args:
            issue_type: Type of issue (bug, security, quality)
            message: Issue message

        Returns:
            List of relevant documentation links
        """
        suggestions = []

        # Security-specific suggestions
        if issue_type == "security":
            if "sql injection" in message.lower():
                suggestions.append(
                    {
                        "title": "SQL Injection Prevention",
                        "url": "https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html",
                        "description": "OWASP SQL injection prevention guide",
                    }
                )

            if "xss" in message.lower() or "cross-site scripting" in message.lower():
                suggestions.append(
                    {
                        "title": "XSS Prevention",
                        "url": "https://cheatsheetseries.owasp.org/cheatsheets/Cross_Site_Scripting_Prevention_Cheat_Sheet.html",
                        "description": "OWASP XSS prevention guide",
                    }
                )

            if "password" in message.lower() or "secret" in message.lower():
                suggestions.append(
                    {
                        "title": "Secrets Management",
                        "url": "https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html",
                        "description": "Best practices for managing secrets",
                    }
                )

            if "command injection" in message.lower():
                suggestions.append(
                    {
                        "title": "Command Injection Prevention",
                        "url": "https://cheatsheetseries.owasp.org/cheatsheets/OS_Command_Injection_Defense_Cheat_Sheet.html",
                        "description": "OWASP command injection defense",
                    }
                )

        # Bug-specific suggestions
        elif issue_type == "bug":
            if "null" in message.lower() or "undefined" in message.lower():
                suggestions.append(
                    {
                        "title": "Null Safety Best Practices",
                        "url": "https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Operators/Optional_chaining",
                        "description": "Handling null and undefined values",
                    }
                )

            if "async" in message.lower() or "promise" in message.lower():
                suggestions.append(
                    {
                        "title": "Async Programming Guide",
                        "url": "https://developer.mozilla.org/en-US/docs/Learn/JavaScript/Asynchronous",
                        "description": "Understanding asynchronous JavaScript",
                    }
                )

        return suggestions

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
        }

        for ext, lang in extension_map.items():
            if filename.endswith(ext):
                return lang

        return "unknown"

    def format_doc_links(self, docs: List[Dict[str, str]]) -> str:
        """
        Format documentation links for display.

        Args:
            docs: List of documentation links

        Returns:
            Formatted string
        """
        if not docs:
            return ""

        formatted = "\n\n📚 **Related Documentation:**\n"
        for doc in docs[:3]:  # Limit to 3 links
            formatted += f"- [{doc['title']}]({doc['url']}) - {doc['description']}\n"

        return formatted
