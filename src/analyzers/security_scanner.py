"""
Security vulnerability scanner.
"""

import re
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)


class SecurityScanner:
    """Scans code for security vulnerabilities."""

    def __init__(self):
        """Initialize security scanner with vulnerability patterns."""
        self.patterns = self._load_security_patterns()

    def _load_security_patterns(self) -> List[Dict[str, Any]]:
        """Load security vulnerability patterns."""
        return [
            # SQL Injection
            {
                "pattern": r'["\'].*(?:SELECT|INSERT|UPDATE|DELETE).*["\'].*%\s',
                "language": "python",
                "message": "Potential SQL injection vulnerability - string formatting in SQL query",
                "severity": "critical",
                "suggestion": "Use parameterized queries with placeholders",
                "type": "security",
                "cwe": "CWE-89",
            },
            {
                "pattern": r'execute\s*\(\s*f["\'].*{.*}.*["\']',
                "language": "python",
                "message": "Potential SQL injection - f-string in SQL query",
                "severity": "critical",
                "suggestion": "Use parameterized queries instead of f-strings",
                "type": "security",
                "cwe": "CWE-89",
            },
            {
                "pattern": r'["\'].*(?:SELECT|INSERT|UPDATE|DELETE).*["\'].*\+',
                "language": "all",
                "message": "Potential SQL injection - string concatenation in query",
                "severity": "critical",
                "suggestion": "Use parameterized queries",
                "type": "security",
                "cwe": "CWE-89",
            },
            # XSS (Cross-Site Scripting)
            {
                "pattern": r"innerHTML\s*=",
                "language": "javascript",
                "message": "Potential XSS vulnerability - using innerHTML",
                "severity": "high",
                "suggestion": "Use textContent or sanitize input with DOMPurify",
                "type": "security",
                "cwe": "CWE-79",
            },
            {
                "pattern": r"dangerouslySetInnerHTML",
                "language": "javascript",
                "message": "Potential XSS vulnerability - dangerouslySetInnerHTML",
                "severity": "high",
                "suggestion": "Sanitize HTML content before rendering",
                "type": "security",
                "cwe": "CWE-79",
            },
            {
                "pattern": r"eval\s*\(",
                "language": "javascript",
                "message": "Use of eval() - major security risk",
                "severity": "critical",
                "suggestion": "Avoid eval(). Use JSON.parse() or safer alternatives",
                "type": "security",
                "cwe": "CWE-95",
            },
            # Hardcoded Secrets
            {
                "pattern": r'(?:password|passwd|pwd)\s*=\s*["\'][^"\']{3,}["\']',
                "language": "all",
                "message": "Hardcoded password detected",
                "severity": "critical",
                "suggestion": "Use environment variables or secure secret management",
                "type": "security",
                "cwe": "CWE-798",
            },
            {
                "pattern": r'(?:api[_-]?key|apikey|api[_-]?secret)\s*=\s*["\'][^"\']{10,}["\']',
                "language": "all",
                "message": "Hardcoded API key detected",
                "severity": "critical",
                "suggestion": "Use environment variables for API keys",
                "type": "security",
                "cwe": "CWE-798",
            },
            {
                "pattern": r'(?:secret[_-]?key|private[_-]?key)\s*=\s*["\'][^"\']{10,}["\']',
                "language": "all",
                "message": "Hardcoded secret key detected",
                "severity": "critical",
                "suggestion": "Use secure secret management system",
                "type": "security",
                "cwe": "CWE-798",
            },
            {
                "pattern": r'(?:token|auth[_-]?token|access[_-]?token)\s*=\s*["\'][^"\']{20,}["\']',
                "language": "all",
                "message": "Hardcoded authentication token detected",
                "severity": "critical",
                "suggestion": "Use environment variables for tokens",
                "type": "security",
                "cwe": "CWE-798",
            },
            # Command Injection
            {
                "pattern": r"os\.system\s*\(",
                "language": "python",
                "message": "Use of os.system() - potential command injection",
                "severity": "high",
                "suggestion": "Use subprocess.run() with shell=False",
                "type": "security",
                "cwe": "CWE-78",
            },
            {
                "pattern": r"subprocess\.\w+\([^)]*shell\s*=\s*True",
                "language": "python",
                "message": "subprocess with shell=True - command injection risk",
                "severity": "high",
                "suggestion": "Use shell=False and pass command as list",
                "type": "security",
                "cwe": "CWE-78",
            },
            {
                "pattern": r"exec\s*\(",
                "language": "python",
                "message": "Use of exec() - code injection risk",
                "severity": "critical",
                "suggestion": "Avoid exec(). Refactor to use safer alternatives",
                "type": "security",
                "cwe": "CWE-95",
            },
            {
                "pattern": r"child_process\.exec\s*\(",
                "language": "javascript",
                "message": "Use of child_process.exec - command injection risk",
                "severity": "high",
                "suggestion": "Use execFile() or spawn() with argument array",
                "type": "security",
                "cwe": "CWE-78",
            },
            # Path Traversal
            {
                "pattern": r"open\s*\([^)]*\+[^)]*\)",
                "language": "python",
                "message": "Potential path traversal - concatenating user input to file path",
                "severity": "high",
                "suggestion": "Validate and sanitize file paths, use os.path.join()",
                "type": "security",
                "cwe": "CWE-22",
            },
            {
                "pattern": r"readFile\s*\([^)]*\+[^)]*\)",
                "language": "javascript",
                "message": "Potential path traversal - concatenating paths",
                "severity": "high",
                "suggestion": "Use path.join() and validate input",
                "type": "security",
                "cwe": "CWE-22",
            },
            # Insecure Cryptography
            {
                "pattern": r"md5\s*\(",
                "language": "all",
                "message": "MD5 is cryptographically broken",
                "severity": "high",
                "suggestion": "Use SHA-256 or stronger hash functions",
                "type": "security",
                "cwe": "CWE-327",
            },
            {
                "pattern": r"sha1\s*\(",
                "language": "all",
                "message": "SHA-1 is deprecated for security purposes",
                "severity": "medium",
                "suggestion": "Use SHA-256 or SHA-3",
                "type": "security",
                "cwe": "CWE-327",
            },
            {
                "pattern": r"Random\s*\(\)",
                "language": "all",
                "message": "Using non-cryptographic random number generator",
                "severity": "medium",
                "suggestion": "Use secrets module (Python) or crypto.randomBytes (Node.js)",
                "type": "security",
                "cwe": "CWE-338",
            },
            # Insecure Deserialization
            {
                "pattern": r"pickle\.loads?\s*\(",
                "language": "python",
                "message": "Pickle deserialization - arbitrary code execution risk",
                "severity": "critical",
                "suggestion": "Use JSON or validate pickle data source",
                "type": "security",
                "cwe": "CWE-502",
            },
            {
                "pattern": r"yaml\.load\s*\([^)]*(?!Loader)",
                "language": "python",
                "message": "Unsafe YAML loading - code execution risk",
                "severity": "critical",
                "suggestion": "Use yaml.safe_load() instead",
                "type": "security",
                "cwe": "CWE-502",
            },
            # SSRF (Server-Side Request Forgery)
            {
                "pattern": r"requests\.(?:get|post|put|delete)\s*\([^)]*(?:input|request\.|params)",
                "language": "python",
                "message": "Potential SSRF - user input in HTTP request",
                "severity": "high",
                "suggestion": "Validate and whitelist URLs before making requests",
                "type": "security",
                "cwe": "CWE-918",
            },
            {
                "pattern": r"fetch\s*\([^)]*(?:req\.|request\.|params)",
                "language": "javascript",
                "message": "Potential SSRF - user input in fetch request",
                "severity": "high",
                "suggestion": "Validate URLs against whitelist",
                "type": "security",
                "cwe": "CWE-918",
            },
            # Insecure Direct Object Reference
            {
                "pattern": r"\.filter\s*\(\s*id\s*=",
                "language": "python",
                "message": "Potential IDOR - filtering by user-provided ID",
                "severity": "medium",
                "suggestion": "Verify user authorization before accessing objects",
                "type": "security",
                "cwe": "CWE-639",
            },
            # Weak Authentication
            {
                "pattern": r"auth\s*=\s*None",
                "language": "python",
                "message": "Authentication disabled",
                "severity": "high",
                "suggestion": "Enable proper authentication",
                "type": "security",
                "cwe": "CWE-306",
            },
            {
                "pattern": r"verify\s*=\s*False",
                "language": "python",
                "message": "SSL certificate verification disabled",
                "severity": "high",
                "suggestion": "Enable SSL verification for production",
                "type": "security",
                "cwe": "CWE-295",
            },
            # Information Disclosure
            {
                "pattern": r"print\s*\([^)]*(?:password|secret|token|key)",
                "language": "python",
                "message": "Potential information disclosure - printing sensitive data",
                "severity": "medium",
                "suggestion": "Remove or redact sensitive information from logs",
                "type": "security",
                "cwe": "CWE-532",
            },
            {
                "pattern": r"console\.log\s*\([^)]*(?:password|secret|token|key)",
                "language": "javascript",
                "message": "Potential information disclosure - logging sensitive data",
                "severity": "medium",
                "suggestion": "Remove sensitive data from console logs",
                "type": "security",
                "cwe": "CWE-532",
            },
            # Regex DoS
            {
                "pattern": r"re\.compile\s*\([^)]*\([^)]*\+[^)]*\*",
                "language": "python",
                "message": "Potential ReDoS - complex regex with nested quantifiers",
                "severity": "medium",
                "suggestion": "Simplify regex or add timeout",
                "type": "security",
                "cwe": "CWE-1333",
            },
        ]

    def analyze(self, code: str, filename: str) -> List[Dict[str, Any]]:
        """
        Scan code for security vulnerabilities.

        Args:
            code: Source code to scan
            filename: Name of the file

        Returns:
            List of detected vulnerabilities
        """
        vulnerabilities = []
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
                        # Skip if in comment
                        if self._is_in_comment(line, match.start(), language):
                            continue

                        vulnerabilities.append(
                            {
                                "type": pattern_rule["type"],
                                "severity": pattern_rule["severity"],
                                "line": line_num,
                                "column": match.start(),
                                "message": pattern_rule["message"],
                                "suggestion": pattern_rule["suggestion"],
                                "code_snippet": line.strip(),
                                "matched_text": match.group(),
                                "cwe": pattern_rule.get("cwe", "N/A"),
                            }
                        )

            except re.error as e:
                logger.error(f"Regex error in pattern {pattern}: {e}")
                continue

        logger.info(
            f"Security scanner found {len(vulnerabilities)} vulnerabilities in {filename}"
        )
        return vulnerabilities

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

    def _is_in_comment(self, line: str, position: int, language: str) -> bool:
        """Check if position is within a comment."""
        comment_markers = {
            "python": ["#"],
            "javascript": ["//", "/*"],
            "java": ["//", "/*"],
        }

        markers = comment_markers.get(language, [])

        for marker in markers:
            comment_pos = line.find(marker)
            if comment_pos != -1 and comment_pos < position:
                return True

        return False

    def generate_security_report(self, vulnerabilities: List[Dict[str, Any]]) -> str:
        """
        Generate a security report summary.

        Args:
            vulnerabilities: List of detected vulnerabilities

        Returns:
            Formatted security report
        """
        if not vulnerabilities:
            return "✅ No security vulnerabilities detected."

        # Group by severity
        by_severity = {}
        for vuln in vulnerabilities:
            severity = vuln["severity"]
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(vuln)

        report = "## 🔒 Security Scan Results\n\n"

        severity_order = ["critical", "high", "medium", "low"]
        for severity in severity_order:
            if severity in by_severity:
                count = len(by_severity[severity])
                emoji = {"critical": "🚨", "high": "⚠️", "medium": "⚡", "low": "ℹ️"}
                report += (
                    f"{emoji[severity]} **{severity.upper()}**: {count} issue(s)\n"
                )

        return report
