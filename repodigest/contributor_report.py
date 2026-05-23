"""Render a human-readable contributor leaderboard from ContributorStat list."""
from __future__ import annotations

from typing import List

from repodigest.contributor_stats import ContributorStat

_HEADER = "{:<20} {:>7} {:>9} {:>10} {:>10} {:>10}"
_ROW = "{:<20} {:>7} {:>9} {:>10} {:>10} {:>10}"
_DIVIDER = "-" * 72


def render_leaderboard(stats: List[ContributorStat], top_n: int = 10) -> str:
    """Return a formatted leaderboard string for the top N contributors."""
    if not stats:
        return "No contributor data available."

    lines: List[str] = [
        "## Top Contributors",
        _DIVIDER,
        _HEADER.format(
            "Login", "Commits", "PRs Open", "PRs Merged", "Lines +", "Lines -"
        ),
        _DIVIDER,
    ]

    for stat in stats[:top_n]:
        lines.append(
            _ROW.format(
                stat.login[:20],
                stat.commit_count,
                stat.prs_opened,
                stat.prs_merged,
                stat.lines_added,
                stat.lines_deleted,
            )
        )

    lines.append(_DIVIDER)
    lines.append(f"Showing {min(top_n, len(stats))} of {len(stats)} contributors.")
    return "\n".join(lines)


def render_leaderboard_markdown(stats: List[ContributorStat], top_n: int = 10) -> str:
    """Return a Markdown table of the top N contributors."""
    if not stats:
        return "_No contributor data available._"

    rows = [
        "| Login | Commits | PRs Opened | PRs Merged | Lines + | Lines - |",
        "| --- | ---: | ---: | ---: | ---: | ---: |",
    ]
    for stat in stats[:top_n]:
        rows.append(
            f"| {stat.login} | {stat.commit_count} | {stat.prs_opened} "
            f"| {stat.prs_merged} | {stat.lines_added} | {stat.lines_deleted} |"
        )
    return "\n".join(rows)
