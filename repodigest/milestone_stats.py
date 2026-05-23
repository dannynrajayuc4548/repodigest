"""Compute statistics for GitHub milestones within a digest window."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class MilestoneStat:
    title: str
    number: int
    state: str  # "open" | "closed"
    open_issues: int
    closed_issues: int
    due_on: Optional[str]  # ISO date string or None

    @property
    def total_issues(self) -> int:
        return self.open_issues + self.closed_issues

    @property
    def completion_pct(self) -> float:
        if self.total_issues == 0:
            return 0.0
        return round(self.closed_issues / self.total_issues * 100, 1)

    def to_dict(self) -> dict:
        return {
            "title": self.title,
            "number": self.number,
            "state": self.state,
            "open_issues": self.open_issues,
            "closed_issues": self.closed_issues,
            "due_on": self.due_on,
            "completion_pct": self.completion_pct,
        }


def _parse_milestone(raw: dict) -> MilestoneStat:
    return MilestoneStat(
        title=raw.get("title", ""),
        number=raw.get("number", 0),
        state=raw.get("state", "open"),
        open_issues=raw.get("open_issues", 0),
        closed_issues=raw.get("closed_issues", 0),
        due_on=raw.get("due_on"),
    )


def compute_milestone_stats(
    raw_milestones: List[dict],
    state_filter: Optional[str] = None,
) -> List[MilestoneStat]:
    """Parse raw GitHub milestone payloads into MilestoneStat objects.

    Args:
        raw_milestones: List of milestone dicts from the GitHub API.
        state_filter: If provided ("open" or "closed"), only include
                      milestones with that state.

    Returns:
        Sorted list of MilestoneStat, open milestones first, then by number.
    """
    stats = [_parse_milestone(m) for m in raw_milestones]
    if state_filter:
        stats = [s for s in stats if s.state == state_filter]
    stats.sort(key=lambda s: (s.state != "open", s.number))
    return stats
