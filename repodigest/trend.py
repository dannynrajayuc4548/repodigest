"""Compute week-over-week trend metrics for a repository digest."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass
class TrendSnapshot:
    """Captured metric values for a single week."""

    commit_count: int
    merged_prs: int
    open_issues: int
    new_contributors: int


@dataclass
class TrendDelta:
    """Difference between two consecutive weekly snapshots."""

    commit_delta: int
    merged_pr_delta: int
    open_issue_delta: int
    contributor_delta: int

    def commit_direction(self) -> str:
        return _direction(self.commit_delta)

    def pr_direction(self) -> str:
        return _direction(self.merged_pr_delta)

    def issue_direction(self) -> str:
        return _direction(self.open_issue_delta)

    def summary(self) -> str:
        lines = [
            f"Commits      : {_fmt(self.commit_delta)} ({self.commit_direction()})",
            f"Merged PRs   : {_fmt(self.merged_pr_delta)} ({self.pr_direction()})",
            f"Open issues  : {_fmt(self.open_issue_delta)} ({self.issue_direction()})",
            f"Contributors : {_fmt(self.contributor_delta)} ({_direction(self.contributor_delta)})",
        ]
        return "\n".join(lines)


def _direction(value: int) -> str:
    if value > 0:
        return "up"
    if value < 0:
        return "down"
    return "unchanged"


def _fmt(value: int) -> str:
    if value > 0:
        return f"+{value}"
    return str(value)


def compute_trend(
    current: TrendSnapshot,
    previous: Optional[TrendSnapshot],
) -> Optional[TrendDelta]:
    """Return a TrendDelta comparing *current* against *previous*.

    Returns ``None`` when no previous snapshot is available.
    """
    if previous is None:
        return None
    return TrendDelta(
        commit_delta=current.commit_count - previous.commit_count,
        merged_pr_delta=current.merged_prs - previous.merged_prs,
        open_issue_delta=current.open_issues - previous.open_issues,
        contributor_delta=current.new_contributors - previous.new_contributors,
    )


def snapshot_from_digest(digest) -> TrendSnapshot:
    """Build a :class:`TrendSnapshot` from a :class:`~repodigest.digest.Digest`."""
    return TrendSnapshot(
        commit_count=digest.commit_count,
        merged_prs=digest.merged_prs,
        open_issues=digest.open_issues,
        new_contributors=len(digest.top_contributors),
    )
