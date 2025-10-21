"""
GitHub API client for PR operations.
"""

import logging
from typing import List, Optional, Dict, Any
from github import Github, GithubException
from github.PullRequest import PullRequest
from github.File import File
import base64

logger = logging.getLogger(__name__)


class GitHubClient:
    """Client for interacting with GitHub API."""

    def __init__(self, token: str, repo_name: str):
        """
        Initialize GitHub client.

        Args:
            token: GitHub access token
            repo_name: Repository name in format 'owner/repo'
        """
        self.github = Github(token)
        self.repo_name = repo_name
        self.repo = self.github.get_repo(repo_name)
        logger.info(f"Initialized GitHub client for {repo_name}")

    def get_pull_request(self, pr_number: int) -> PullRequest:
        """
        Get pull request by number.

        Args:
            pr_number: PR number

        Returns:
            PullRequest object
        """
        try:
            pr = self.repo.get_pull(pr_number)
            logger.info(f"Retrieved PR #{pr_number}: {pr.title}")
            return pr
        except GithubException as e:
            logger.error(f"Error getting PR #{pr_number}: {e}")
            raise

    def get_pr_files(self, pr_number: int) -> List[File]:
        """
        Get list of files changed in a PR.

        Args:
            pr_number: PR number

        Returns:
            List of File objects
        """
        try:
            pr = self.get_pull_request(pr_number)
            files = list(pr.get_files())
            logger.info(f"Retrieved {len(files)} files from PR #{pr_number}")
            return files
        except GithubException as e:
            logger.error(f"Error getting PR files: {e}")
            raise

    def get_file_content(self, path: str, ref: Optional[str] = None) -> Optional[str]:
        """
        Get content of a file from repository.

        Args:
            path: File path in repository
            ref: Git reference (branch, commit, tag)

        Returns:
            File content as string, or None if not found
        """
        try:
            if ref:
                content = self.repo.get_contents(path, ref=ref)
            else:
                content = self.repo.get_contents(path)

            if isinstance(content, list):
                logger.warning(f"Path {path} is a directory, not a file")
                return None

            # Decode content
            decoded = base64.b64decode(content.content).decode("utf-8")
            logger.info(f"Retrieved content for {path} ({len(decoded)} chars)")
            return decoded

        except GithubException as e:
            if e.status == 404:
                logger.warning(f"File not found: {path}")
            else:
                logger.error(f"Error getting file content for {path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Error decoding file {path}: {e}")
            return None

    def create_review_comment(
        self, pr_number: int, body: str, path: str, line: int, side: str = "RIGHT"
    ) -> bool:
        """
        Create a review comment on a specific line.

        Args:
            pr_number: PR number
            body: Comment body
            path: File path
            line: Line number
            side: Side of diff (LEFT or RIGHT)

        Returns:
            True if successful, False otherwise
        """
        try:
            pr = self.get_pull_request(pr_number)
            commit = pr.get_commits().reversed[0]  # Latest commit

            pr.create_review_comment(
                body=body, commit=commit, path=path, line=line, side=side
            )

            logger.info(f"Created review comment on {path}:{line}")
            return True

        except GithubException as e:
            logger.error(f"Error creating review comment: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error creating review comment: {e}")
            return False

    def create_issue_comment(self, pr_number: int, body: str) -> bool:
        """
        Create a general comment on the PR.

        Args:
            pr_number: PR number
            body: Comment body

        Returns:
            True if successful, False otherwise
        """
        try:
            pr = self.get_pull_request(pr_number)
            pr.create_issue_comment(body)
            logger.info(f"Created issue comment on PR #{pr_number}")
            return True

        except GithubException as e:
            logger.error(f"Error creating issue comment: {e}")
            return False

    def create_review(
        self,
        pr_number: int,
        body: str,
        event: str = "COMMENT",
        comments: Optional[List[Dict[str, Any]]] = None,
    ) -> bool:
        """
        Create a PR review with multiple comments.

        Args:
            pr_number: PR number
            body: Review body
            event: Review event (APPROVE, REQUEST_CHANGES, COMMENT)
            comments: List of review comments

        Returns:
            True if successful, False otherwise
        """
        try:
            pr = self.get_pull_request(pr_number)
            commit = pr.get_commits().reversed[0]

            if comments:
                pr.create_review(
                    commit=commit, body=body, event=event, comments=comments
                )
            else:
                pr.create_review(commit=commit, body=body, event=event)

            logger.info(f"Created review on PR #{pr_number}")
            return True

        except GithubException as e:
            logger.error(f"Error creating review: {e}")
            return False

    def add_labels(self, pr_number: int, labels: List[str]) -> bool:
        """
        Add labels to a PR.

        Args:
            pr_number: PR number
            labels: List of label names

        Returns:
            True if successful, False otherwise
        """
        try:
            issue = self.repo.get_issue(pr_number)
            issue.add_to_labels(*labels)
            logger.info(f"Added labels {labels} to PR #{pr_number}")
            return True

        except GithubException as e:
            logger.error(f"Error adding labels: {e}")
            return False

    def get_pr_diff(self, pr_number: int) -> Optional[str]:
        """
        Get the full diff for a PR.

        Args:
            pr_number: PR number

        Returns:
            Diff as string, or None if error
        """
        try:
            pr = self.get_pull_request(pr_number)
            # Get diff using raw API
            diff_url = pr.diff_url
            import requests

            response = requests.get(diff_url)

            if response.status_code == 200:
                logger.info(f"Retrieved diff for PR #{pr_number}")
                return response.text
            else:
                logger.error(f"Error getting diff: status {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Error getting PR diff: {e}")
            return None

    def get_pr_commits(self, pr_number: int) -> List[Any]:
        """
        Get list of commits in a PR.

        Args:
            pr_number: PR number

        Returns:
            List of commit objects
        """
        try:
            pr = self.get_pull_request(pr_number)
            commits = list(pr.get_commits())
            logger.info(f"Retrieved {len(commits)} commits from PR #{pr_number}")
            return commits
        except GithubException as e:
            logger.error(f"Error getting PR commits: {e}")
            return []

    def update_pr_status(
        self,
        pr_number: int,
        state: str,
        description: str,
        context: str = "pr-review-bot",
    ) -> bool:
        """
        Update PR status check.

        Args:
            pr_number: PR number
            state: Status state (pending, success, failure, error)
            description: Status description
            context: Status context/name

        Returns:
            True if successful, False otherwise
        """
        try:
            pr = self.get_pull_request(pr_number)
            commit = pr.get_commits().reversed[0]

            commit.create_status(state=state, description=description, context=context)

            logger.info(f"Updated PR status: {state} - {description}")
            return True

        except GithubException as e:
            logger.error(f"Error updating PR status: {e}")
            return False
