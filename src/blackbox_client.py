"""
Blackbox API client for code analysis.
"""

import logging
import requests
from typing import Dict, Any, Optional
import time

logger = logging.getLogger(__name__)


class BlackboxClient:
    """Client for interacting with Blackbox API."""

    def __init__(self, api_key: str):
        """
        Initialize Blackbox client.

        Args:
            api_key: Blackbox API key
        """
        self.api_key = api_key
        self.base_url = "https://www.blackbox.ai/api/chat"
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})

        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.5  # seconds between requests

    def _rate_limit(self):
        """Implement rate limiting."""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time

        if time_since_last_request < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last_request
            time.sleep(sleep_time)

        self.last_request_time = time.time()

    def analyze_code(self, prompt: str, max_retries: int = 3) -> str:
        """
        Analyze code using Blackbox API.

        Args:
            prompt: The analysis prompt containing code and instructions
            max_retries: Maximum number of retry attempts

        Returns:
            Analysis result as string
        """
        self._rate_limit()

        payload = {
            "messages": [{"id": "user-msg", "content": prompt, "role": "user"}],
            "id": "chat-id",
            "previewToken": self.api_key,
            "userId": None,
            "codeModelMode": True,
            "agentMode": {},
            "trendingAgentMode": {},
            "isMicMode": False,
            "userSystemPrompt": None,
            "maxTokens": 1024,
            "playgroundTopP": None,
            "playgroundTemperature": None,
            "isChromeExt": False,
            "githubToken": None,
            "clickedAnswer2": False,
            "clickedAnswer3": False,
            "clickedForceWebSearch": False,
            "visitFromDelta": False,
            "mobileClient": False,
            "userSelectedModel": None,
            "validated": self.api_key,
        }

        for attempt in range(max_retries):
            try:
                logger.info(
                    f"Sending request to Blackbox API (attempt {attempt + 1}/{max_retries})"
                )

                response = self.session.post(self.base_url, json=payload, timeout=60)

                if response.status_code == 200:
                    result = response.text
                    logger.info(
                        f"Received response from Blackbox API ({len(result)} chars)"
                    )
                    return result
                elif response.status_code == 429:
                    # Rate limited
                    retry_after = int(response.headers.get("Retry-After", 5))
                    logger.warning(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                    continue
                else:
                    logger.error(
                        f"API request failed with status {response.status_code}: {response.text}"
                    )
                    if attempt < max_retries - 1:
                        time.sleep(2**attempt)  # Exponential backoff
                        continue

            except requests.exceptions.Timeout:
                logger.error(f"Request timeout (attempt {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)
                    continue

            except Exception as e:
                logger.error(f"Error calling Blackbox API: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2**attempt)
                    continue

        # If all retries failed, return empty response
        logger.error("All retry attempts failed")
        return ""

    def analyze_diff(self, diff: str, context: str = "") -> str:
        """
        Analyze a code diff.

        Args:
            diff: Git diff string
            context: Additional context about the changes

        Returns:
            Analysis result
        """
        prompt = f"""Analyze this code diff for potential issues:

Context: {context}

Diff:
```diff
{diff}
```

Focus on:
1. New bugs introduced
2. Security vulnerabilities
3. Breaking changes
4. Performance impacts
5. Code quality issues

Provide specific line numbers and actionable suggestions."""

        return self.analyze_code(prompt)

    def suggest_improvements(self, code: str, language: str) -> str:
        """
        Suggest improvements for code.

        Args:
            code: Source code
            language: Programming language

        Returns:
            Improvement suggestions
        """
        prompt = f"""Suggest improvements for this {language} code:

```{language}
{code}
```

Provide:
1. Code quality improvements
2. Performance optimizations
3. Best practice recommendations
4. Refactoring suggestions

Be specific and provide code examples."""

        return self.analyze_code(prompt)

    def explain_code(self, code: str, language: str) -> str:
        """
        Generate explanation for code.

        Args:
            code: Source code
            language: Programming language

        Returns:
            Code explanation
        """
        prompt = f"""Explain what this {language} code does:

```{language}
{code}
```

Provide:
1. High-level overview
2. Key functionality
3. Important details
4. Potential concerns"""

        return self.analyze_code(prompt)

    def check_security(self, code: str, language: str) -> str:
        """
        Perform security analysis on code.

        Args:
            code: Source code
            language: Programming language

        Returns:
            Security analysis
        """
        prompt = f"""Perform a security analysis on this {language} code:

```{language}
{code}
```

Check for:
1. SQL injection vulnerabilities
2. XSS vulnerabilities
3. Authentication/authorization issues
4. Sensitive data exposure
5. Insecure dependencies
6. Cryptographic weaknesses
7. Input validation issues

Provide severity levels and remediation steps."""

        return self.analyze_code(prompt)
