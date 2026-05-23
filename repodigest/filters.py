"""Filtering utilities for GitHub activity data."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class FilterConfig:
    """Criteria used to narrow down activity items."""

    authors: List[str] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)
    exclude_bots: bool = True
    min_additions: Optional[int] = None
    min_deletions: Optional[int] = None

    # Known bot suffixes / names
    _BOT_SUFFIXES: List[str] = field(
        default_factory=lambda: ["[bot]", "-bot", "_bot"],
        repr=False,
        compare=False,
    )

    def is_bot(self, login: str) -> bool:
        """Return True when *login* looks like an automated bot account."""
        lower = login.lower()
        return any(lower.endswith(suffix) for suffix in self._BOT_SUFFIXES)

    def match_commit(self, commit: dict) -> bool:
        """Return True when *commit* passes all active filters."""
        author = (commit.get("author") or {}).get("login", "")
        if self.exclude_bots and self.is_bot(author):
            return False
        if self.authors and author not in self.authors:
            return False
        stats = commit.get("stats") or {}
        if self.min_additions is not None and stats.get("additions", 0) < self.min_additions:
            return False
        if self.min_deletions is not None and stats.get("deletions", 0) < self.min_deletions:
            return False
        return True

    def match_pr(self, pr: dict) -> bool:
        """Return True when *pr* passes all active filters."""
        author = (pr.get("user") or {}).get("login", "")
        if self.exclude_bots and self.is_bot(author):
            return False
        if self.authors and author not in self.authors:
            return False
        if self.labels:
            pr_labels = {lbl["name"] for lbl in (pr.get("labels") or [])}
            if not pr_labels.intersection(self.labels):
                return False
        return True

    def match_issue(self, issue: dict) -> bool:
        """Return True when *issue* passes all active filters."""
        author = (issue.get("user") or {}).get("login", "")
        if self.exclude_bots and self.is_bot(author):
            return False
        if self.authors and author not in self.authors:
            return False
        if self.labels:
            issue_labels = {lbl["name"] for lbl in (issue.get("labels") or [])}
            if not issue_labels.intersection(self.labels):
                return False
        return True


def apply_filters(items: list, filter_fn) -> list:
    """Return a new list containing only items for which *filter_fn* returns True."""
    return [item for item in items if filter_fn(item)]
