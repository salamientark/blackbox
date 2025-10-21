#!/usr/bin/env python3
"""
Main entry point for the PR Review Bot.
Orchestrates the entire review process.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any

from github_client import GitHubClient
from blackbox_client import BlackboxClient
from analyzers.bug_detector import BugDetector
from analyzers.security_scanner import SecurityScanner
from analyzers.doc_linker import DocLinker
from analyzers.summarizer import Summarizer
from utils.diff_parser import DiffParser
from utils.comment_formatter import CommentFormatter

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class PRReviewBot:
    """Main PR Review Bot orchestrator."""

    def __init__(self):
        """Initialize the bot with necessary clients and analyzers."""
        self.github_client = GitHubClient(
            token=os.getenv("GITHUB_TOKEN"), repo_name=os.getenv("REPO_NAME")
        )
        self.blackbox_client = BlackboxClient(api_key=os.getenv("BLACKBOX_API_KEY"))

        # Initialize analyzers
        self.bug_detector = BugDetector()
        self.security_scanner = SecurityScanner()
        self.doc_linker = DocLinker()
        self.summarizer = Summarizer()

        self.diff_parser = DiffParser()
        self.comment_formatter = CommentFormatter()

        self.pr_number = int(os.getenv("PR_NUMBER", 0))
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from repository or use defaults."""
        try:
            config_content = self.github_client.get_file_content(".pr-review-bot.json")
            if config_content:
                return json.loads(config_content)
        except Exception as e:
            logger.warning(f"Could not load config file: {e}")

        # Default configuration
        return {
            "enabled": True,
            "auto_comment": True,
            "severity_threshold": "low",
            "ignore_patterns": ["*.md", "*.txt", "package-lock.json", "yarn.lock"],
            "features": {
                "bug_detection": True,
                "security_scan": True,
                "doc_linking": True,
                "summarization": True,
            },
            "max_comments": 50,
        }

    def should_ignore_file(self, filename: str) -> bool:
        """Check if file should be ignored based on patterns."""
        import fnmatch

        for pattern in self.config.get("ignore_patterns", []):
            if fnmatch.fnmatch(filename, pattern):
                return True
        return False

    def analyze_code_with_blackbox(
        self, code: str, filename: str, context: str = ""
    ) -> Dict[str, Any]:
        """Analyze code using Blackbox API with fallback to local analysis."""
        try:
            prompt = f"""Analyze this code for potential issues, bugs, and improvements.

File: {filename}
Context: {context}

Code:
```
{code}
```

Please provide:
1. Potential bugs or logic errors
2. Security vulnerabilities
3. Code quality issues
4. Performance concerns
5. Best practice violations
6. Suggestions for improvement

Format your response as JSON with this structure:
{{
    "issues": [
        {{
            "type": "bug|security|quality|performance",
            "severity": "critical|high|medium|low|info",
            "line": <line_number>,
            "message": "Description of the issue",
            "suggestion": "How to fix it",
            "code_snippet": "Suggested code fix"
        }}
    ],
    "summary": "Overall assessment"
}}
"""

            response = self.blackbox_client.analyze_code(prompt)

            # Check if response is valid
            if response and len(response) > 50 and "Login to continue" not in response:
                return self._parse_blackbox_response(response)
            else:
                logger.warning(
                    "Blackbox API returned invalid response, using local analysis only"
                )
                return {"issues": [], "summary": "Using local pattern-based analysis"}

        except Exception as e:
            logger.error(f"Error analyzing code with Blackbox: {e}")
            return {"issues": [], "summary": "Using local pattern-based analysis"}

    def _parse_blackbox_response(self, response: str) -> Dict[str, Any]:
        """Parse Blackbox API response."""
        try:
            # Try to extract JSON from response
            import re

            json_match = re.search(r"\{.*\}", response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())

            # Fallback: create structured response from text
            return {"issues": [], "summary": response[:500]}  # First 500 chars
        except Exception as e:
            logger.error(f"Error parsing Blackbox response: {e}")
            return {"issues": [], "summary": response[:500] if response else ""}

    def run_local_analyzers(self, code: str, filename: str) -> List[Dict[str, Any]]:
        """Run local pattern-based analyzers."""
        issues = []

        if self.config["features"].get("bug_detection", True):
            issues.extend(self.bug_detector.analyze(code, filename))

        if self.config["features"].get("security_scan", True):
            issues.extend(self.security_scanner.analyze(code, filename))

        return issues

    def process_pr(self):
        """Main process to review the PR."""
        try:
            logger.info(f"Starting PR review for PR #{self.pr_number}")

            if not self.config.get("enabled", True):
                logger.info("Bot is disabled in configuration")
                return

            # Get PR details
            pr = self.github_client.get_pull_request(self.pr_number)
            logger.info(f"Reviewing PR: {pr.title}")

            # Get changed files
            files = self.github_client.get_pr_files(self.pr_number)
            logger.info(f"Found {len(files)} changed files")

            all_issues = []
            file_analyses = []

            # Analyze each file
            for file in files:
                if self.should_ignore_file(file.filename):
                    logger.info(f"Skipping ignored file: {file.filename}")
                    continue

                if file.status == "removed":
                    continue

                logger.info(f"Analyzing file: {file.filename}")

                try:
                    # Get file content
                    content = self.github_client.get_file_content(
                        file.filename, ref=os.getenv("HEAD_SHA")
                    )

                    if not content:
                        continue

                    # Parse diff to get changed lines
                    changed_lines = (
                        self.diff_parser.parse_patch(file.patch) if file.patch else []
                    )

                    # Run Blackbox analysis
                    blackbox_result = self.analyze_code_with_blackbox(
                        content,
                        file.filename,
                        context=f"PR: {pr.title}\nChanges: {file.additions} additions, {file.deletions} deletions",
                    )

                    # Run local analyzers
                    local_issues = self.run_local_analyzers(content, file.filename)

                    # Combine issues
                    file_issues = blackbox_result.get("issues", []) + local_issues

                    # Add documentation links
                    if self.config["features"].get("doc_linking", True):
                        for issue in file_issues:
                            doc_links = self.doc_linker.find_relevant_docs(
                                issue.get("message", ""), file.filename
                            )
                            issue["doc_links"] = doc_links

                    # Filter by severity threshold
                    severity_order = ["info", "low", "medium", "high", "critical"]
                    threshold_idx = severity_order.index(
                        self.config.get("severity_threshold", "low")
                    )

                    filtered_issues = [
                        issue
                        for issue in file_issues
                        if severity_order.index(issue.get("severity", "info"))
                        >= threshold_idx
                    ]

                    file_analyses.append(
                        {
                            "filename": file.filename,
                            "issues": filtered_issues,
                            "summary": blackbox_result.get("summary", ""),
                            "stats": {
                                "additions": file.additions,
                                "deletions": file.deletions,
                                "changes": file.changes,
                            },
                        }
                    )

                    all_issues.extend(filtered_issues)

                except Exception as e:
                    logger.error(f"Error analyzing file {file.filename}: {e}")
                    continue

            # Post comments
            if self.config.get("auto_comment", True) and all_issues:
                self._post_review_comments(file_analyses)

            # Generate and post summary
            if self.config["features"].get("summarization", True):
                summary = self.summarizer.generate_summary(
                    pr_title=pr.title,
                    pr_description=pr.body or "",
                    file_analyses=file_analyses,
                    total_files=len(files),
                )
                self._post_summary_comment(summary)

            # Save results
            self._save_results(file_analyses, all_issues)

            logger.info(f"PR review completed. Found {len(all_issues)} issues.")

        except Exception as e:
            logger.error(f"Error processing PR: {e}", exc_info=True)
            sys.exit(1)

    def _post_review_comments(self, file_analyses: List[Dict[str, Any]]):
        """Post inline review comments on the PR."""
        comment_count = 0
        max_comments = self.config.get("max_comments", 50)

        for file_analysis in file_analyses:
            filename = file_analysis["filename"]

            for issue in file_analysis["issues"]:
                if comment_count >= max_comments:
                    logger.warning(f"Reached maximum comment limit ({max_comments})")
                    break

                try:
                    comment_body = self.comment_formatter.format_issue(issue)

                    # Post comment on specific line if available
                    line = issue.get("line")
                    if line:
                        self.github_client.create_review_comment(
                            pr_number=self.pr_number,
                            body=comment_body,
                            path=filename,
                            line=line,
                        )
                        comment_count += 1
                        logger.info(f"Posted comment on {filename}:{line}")

                except Exception as e:
                    logger.error(f"Error posting comment: {e}")
                    continue

            if comment_count >= max_comments:
                break

    def _post_summary_comment(self, summary: str):
        """Post a summary comment on the PR."""
        try:
            self.github_client.create_issue_comment(
                pr_number=self.pr_number, body=summary
            )
            logger.info("Posted summary comment")
        except Exception as e:
            logger.error(f"Error posting summary: {e}")

    def _save_results(
        self, file_analyses: List[Dict[str, Any]], all_issues: List[Dict[str, Any]]
    ):
        """Save analysis results to files."""
        try:
            # Save detailed results
            with open("analysis-results.json", "w") as f:
                json.dump(
                    {
                        "pr_number": self.pr_number,
                        "file_analyses": file_analyses,
                        "total_issues": len(all_issues),
                        "config": self.config,
                    },
                    f,
                    indent=2,
                )

            logger.info("Saved analysis results to analysis-results.json")

        except Exception as e:
            logger.error(f"Error saving results: {e}")


def main():
    """Main entry point."""
    # Validate environment variables
    required_vars = ["GITHUB_TOKEN", "BLACKBOX_API_KEY", "PR_NUMBER", "REPO_NAME"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(
            f"Missing required environment variables: {', '.join(missing_vars)}"
        )
        sys.exit(1)

    # Run the bot
    bot = PRReviewBot()
    bot.process_pr()


if __name__ == "__main__":
    main()
