"""GitHub API client with optional file-based caching."""

import os
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

import requests

from repodigest.cache import Cache

BASE_URL = "https://api.github.com"
DEFAULT_LOOKBACK_DAYS = 7


class GitHubClient:
    """Thin wrapper around the GitHub REST API."""

    def __init__(
        self,
        token: Optional[str] = None,
        use_cache: bool = True,
        cache_ttl: int = 3600,
    ):
        self.token = token or os.environ.get("GITHUB_TOKEN")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        if self.token:
            self.session.headers["Authorization"] = f"Bearer {self.token}"
        self.cache: Optional[Cache] = Cache(ttl=cache_ttl) if use_cache else None

    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        url = f"{BASE_URL}{path}"
        cache_key = path + ("?" + "&".join(f"{k}={v}" for k, v in sorted((params or {}).items())) if params else "")
        if self.cache:
            cached = self.cache.get(cache_key)
            if cached is not None:
                return cached
        response = self.session.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if self.cache:
            self.cache.set(cache_key, data)
        return data

    def _since(self, days: int = DEFAULT_LOOKBACK_DAYS) -> str:
        dt = datetime.now(timezone.utc) - timedelta(days=days)
        return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_commits(self, repo: str, days: int = DEFAULT_LOOKBACK_DAYS) -> List[Dict]:
        return self._get(f"/repos/{repo}/commits", {"since": self._since(days), "per_page": 100})

    def get_pull_requests(self, repo: str, state: str = "all") -> List[Dict]:
        return self._get(f"/repos/{repo}/pulls", {"state": state, "per_page": 100, "sort": "updated", "direction": "desc"})

    def get_issues(self, repo: str, state: str = "open") -> List[Dict]:
        return self._get(f"/repos/{repo}/issues", {"state": state, "per_page": 100, "sort": "updated"})

    def get_releases(self, repo: str) -> List[Dict]:
        return self._get(f"/repos/{repo}/releases", {"per_page": 10})

    def get_repo(self, repo: str) -> Dict:
        return self._get(f"/repos/{repo}")

    def get_contributors(self, repo: str) -> List[Dict]:
        return self._get(f"/repos/{repo}/contributors", {"per_page": 10})
