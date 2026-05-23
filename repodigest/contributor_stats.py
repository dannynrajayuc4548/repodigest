"""Aggregate per-contributor statistics from digest data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ContributorStat:
    login: str
    commit_count: int = 0
    prs_opened: int = 0
    prs_merged: int = 0
    lines_added: int = 0
    lines_deleted: int = 0

    @property
    def total_changes(self) -> int:
        return self.lines_added + self.lines_deleted

    def to_dict(self) -> dict:
        return {
            "login": self.login,
            "commit_count": self.commit_count,
            "prs_opened": self.prs_opened,
            "prs_merged": self.prs_merged,
            "lines_added": self.lines_added,
            "lines_deleted": self.lines_deleted,
            "total_changes": self.total_changes,
        }


def compute_contributor_stats(
    commits: List[dict],
    prs: List[dict],
    diff_details: List[dict] | None = None,
) -> List[ContributorStat]:
    """Return a list of ContributorStat sorted by commit_count descending."""
    stats: Dict[str, ContributorStat] = {}

    def _get(login: str) -> ContributorStat:
        if login not in stats:
            stats[login] = ContributorStat(login=login)
        return stats[login]

    for commit in commits:
        author = (commit.get("author") or {}).get("login") or (
            commit.get("commit", {}).get("author", {}).get("name", "unknown")
        )
        _get(author).commit_count += 1

    for pr in prs:
        login = (pr.get("user") or {}).get("login", "unknown")
        _get(login).prs_opened += 1
        if pr.get("merged_at"):
            _get(login).prs_merged += 1

    if diff_details:
        for detail in diff_details:
            login = (detail.get("author") or {}).get("login") or "unknown"
            _get(login).lines_added += detail.get("stats", {}).get("additions", 0)
            _get(login).lines_deleted += detail.get("stats", {}).get("deletions", 0)

    return sorted(stats.values(), key=lambda s: s.commit_count, reverse=True)
