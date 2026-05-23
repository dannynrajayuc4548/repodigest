"""Aggregate label usage statistics across PRs and issues."""
from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import List, Dict, Sequence


@dataclass
class LabelStat:
    name: str
    count: int
    pr_count: int
    issue_count: int

    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "count": self.count,
            "pr_count": self.pr_count,
            "issue_count": self.issue_count,
        }


def _extract_label_names(item: dict) -> List[str]:
    """Return label name strings from a PR or issue dict."""
    labels = item.get("labels") or []
    return [lbl["name"] for lbl in labels if isinstance(lbl, dict) and "name" in lbl]


def compute_label_stats(
    prs: Sequence[dict],
    issues: Sequence[dict],
    top_n: int = 10,
) -> List[LabelStat]:
    """Return the *top_n* most-used labels across PRs and issues.

    Args:
        prs: Raw PR dicts as returned by the GitHub API.
        issues: Raw issue dicts as returned by the GitHub API.
        top_n: Maximum number of labels to return, sorted by total count desc.

    Returns:
        List of :class:`LabelStat` ordered by descending total count.
    """
    pr_counter: Counter = Counter()
    issue_counter: Counter = Counter()

    for pr in prs:
        for name in _extract_label_names(pr):
            pr_counter[name] += 1

    for issue in issues:
        for name in _extract_label_names(issue):
            issue_counter[name] += 1

    all_labels = set(pr_counter) | set(issue_counter)
    stats = [
        LabelStat(
            name=label,
            count=pr_counter[label] + issue_counter[label],
            pr_count=pr_counter[label],
            issue_count=issue_counter[label],
        )
        for label in all_labels
    ]
    stats.sort(key=lambda s: (-s.count, s.name))
    return stats[:top_n]
