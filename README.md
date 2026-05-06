# blackbox

> Automated PR review bot powered by the Blackbox AI API and local static analyzers. Drop it into any GitHub repository and get inline review comments on every pull request.

`blackbox` runs as a GitHub Action on each pull request, analyzes the diff with the Blackbox AI API, augments results with local pattern-based analyzers (bugs, security, doc links), and posts inline + summary comments back on the PR.

## Features

- **AI-assisted review** — sends changed files to the Blackbox AI API for bug, security, quality, and performance feedback
- **Local analyzers** — pattern-based bug detection and security scanning that work even if the API is unavailable
- **Inline comments** — issues posted on the exact line, with severity, suggestion, and code snippet
- **PR summary** — one consolidated summary comment per PR
- **Doc linking** — relevant documentation references attached to issues
- **Configurable** — severity threshold, ignore patterns, max comments, feature toggles via `.pr-review-bot.json`
- **Resilient** — retries, exponential backoff, rate-limit handling, graceful fallback to local analysis

## How it works

```
PR opened/updated
      │
      ▼
GitHub Action (.github/workflows/pr-review.yml)
      │
      ▼
src/main.py  ──►  GitHubClient   (fetch PR, files, diff)
                  BlackboxClient (AI analysis)
                  Analyzers      (bug / security / doc / summary)
      │
      ▼
Inline review comments + summary + analysis-results.json artifact
```

## Quick start

### 1. Add the workflow

Copy this repository's `.github/workflows/pr-review.yml` into the target repo. It triggers on `pull_request` events.

### 2. Configure secrets

In the target repo, add these GitHub Actions secrets:

| Secret | Required | Purpose |
|--------|----------|---------|
| `BLACKBOX_API_KEY` | yes | Blackbox AI API token |
| `GITHUB_TOKEN` | provided | Auto-injected by Actions |

### 3. (Optional) Tune behavior

Add `.pr-review-bot.json` at the repo root:

```json
{
  "enabled": true,
  "auto_comment": true,
  "severity_threshold": "low",
  "ignore_patterns": ["*.md", "*.txt", "package-lock.json", "*.min.js"],
  "features": {
    "bug_detection": true,
    "security_scan": true,
    "doc_linking": true,
    "summarization": true
  },
  "max_comments": 50
}
```

| Key | Description |
|-----|-------------|
| `enabled` | Master switch |
| `auto_comment` | Post inline comments automatically |
| `severity_threshold` | Min severity to report: `info`, `low`, `medium`, `high`, `critical` |
| `ignore_patterns` | Glob patterns of files to skip |
| `features.*` | Toggle individual analyzers |
| `max_comments` | Cap inline comments per PR |

## Local development

```bash
git clone <repo>
cd blackbox
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
```

Run against a PR locally:

```bash
export GITHUB_TOKEN=ghp_...
export BLACKBOX_API_KEY=...
export REPO_NAME=owner/repo
export PR_NUMBER=123
export HEAD_SHA=$(git rev-parse HEAD)

python src/main.py
```

> [!NOTE]
> The bot writes `analysis-results.json` to the working directory when it finishes. The GitHub Action uploads it as a build artifact for 30 days.

## Project layout

```
src/
├── main.py              # Orchestrator
├── github_client.py     # PyGithub wrapper (fetch PR, post comments)
├── blackbox_client.py   # Blackbox AI HTTP client (retries, rate limit)
├── analyzers/
│   ├── bug_detector.py
│   ├── security_scanner.py
│   ├── doc_linker.py
│   └── summarizer.py
└── utils/
    ├── diff_parser.py
    └── comment_formatter.py
```

## Requirements

- Python 3.11+
- A repo with GitHub Actions enabled
- A Blackbox AI API key

## Testing

```bash
pytest --cov=src --cov-report=term-missing
```

> [!WARNING]
> The bot posts comments with the identity of the `GITHUB_TOKEN` it runs under. Verify token permissions (`pull-requests: write`, `issues: write`) before enabling on production repos.
