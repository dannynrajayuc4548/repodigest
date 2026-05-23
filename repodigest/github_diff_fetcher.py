"""Fetch per-commit diff details from the GitHub API for a list of SHAs."""

from __future__ import annotations

from typing import List, Dict, Optional

from repodigest.github_client import GitHubClient


def fetch_commit_details(
    client: GitHubClient,
    repo: str,
    shas: List[str],
    max_commits: int = 50,
) -> List[Dict]:
    """Return detailed commit payloads (including ``stats`` and ``files``) for
    up to *max_commits* SHAs.

    Silently skips any SHA that returns a non-200 response so that a single
    missing commit does not abort the entire run.
    """
    details: List[Dict] = []
    for sha in shas[:max_commits]:
        try:
            data: Optional[Dict] = client._get(f"/repos/{repo}/commits/{sha}")
            if data:
                details.append(data)
        except Exception:
            # Best-effort: skip commits that cannot be fetched
            continue
    return details


def diff_stats_for_repo(
    client: GitHubClient,
    repo: str,
    commits: List[Dict],
    max_commits: int = 50,
) -> List[Dict]:
    """Convenience wrapper: extract SHAs from *commits* list items and fetch
    their detailed payloads.

    *commits* is the list returned by ``GitHubClient.get_commits``.
    """
    shas = [
        c.get("sha", "") or c.get("id", "")
        for c in commits
        if c.get("sha") or c.get("id")
    ]
    return fetch_commit_details(client, repo, shas, max_commits=max_commits)
