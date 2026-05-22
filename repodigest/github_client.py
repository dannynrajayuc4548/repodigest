"""GitHub API client for fetching repository activity."""

from datetime import datetime, timedelta, timezone
from typing import Any

import requests

GITHUB_API_BASE = "https://api.github.com"
DEFAULT_HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}


class GitHubClient:
    """Thin wrapper around the GitHub REST API."""

    def __init__(self, token: str | None = None) -> None:
        self.session = requests.Session()
        self.session.headers.update(DEFAULT_HEADERS)
        if token:
            self.session.headers["Authorization"] = f"Bearer {token}"

    def _get(self, path: str, params: dict | None = None) -> Any:
        url = f"{GITHUB_API_BASE}{path}"
        response = self.session.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()

    def get_commits(self, owner: str, repo: str, since: datetime) -> list[dict]:
        """Return commits pushed after *since*."""
        return self._get(
            f"/repos/{owner}/{repo}/commits",
            params={"since": since.isoformat()},
        )

    def get_pull_requests(self, owner: str, repo: str, since: datetime) -> list[dict]:
        """Return pull requests updated after *since*."""
        prs = self._get(
            f"/repos/{owner}/{repo}/pulls",
            params={"state": "all", "sort": "updated", "direction": "desc", "per_page": 50},
        )
        return [pr for pr in prs if datetime.fromisoformat(pr["updated_at"].rstrip("Z")).replace(tzinfo=timezone.utc) >= since]

    def get_issues(self, owner: str, repo: str, since: datetime) -> list[dict]:
        """Return issues (excluding PRs) updated after *since*."""
        items = self._get(
            f"/repos/{owner}/{repo}/issues",
            params={"state": "all", "since": since.isoformat(), "per_page": 50},
        )
        return [i for i in items if "pull_request" not in i]

    def get_releases(self, owner: str, repo: str) -> list[dict]:
        """Return the five most recent releases."""
        return self._get(f"/repos/{owner}/{repo}/releases", params={"per_page": 5})


def week_ago() -> datetime:
    """Return a timezone-aware datetime representing exactly one week ago."""
    return datetime.now(tz=timezone.utc) - timedelta(weeks=1)
