"""Render milestone statistics as text or Markdown."""
from __future__ import annotations

from typing import List

from repodigest.milestone_stats import MilestoneStat

_BAR_WIDTH = 20


def _progress_bar(pct: float, width: int = _BAR_WIDTH) -> str:
    """Return an ASCII progress bar string for the given percentage."""
    filled = round(pct / 100 * width)
    return "[" + "#" * filled + "-" * (width - filled) + "]"


def render_milestones_text(stats: List[MilestoneStat]) -> str:
    """Render milestone stats as a plain-text block."""
    if not stats:
        return "No milestones found.\n"

    lines: List[str] = ["Milestones", "=" * 40]
    for ms in stats:
        due = f"  due: {ms.due_on}" if ms.due_on else ""
        bar = _progress_bar(ms.completion_pct)
        lines.append(
            f"  #{ms.number} [{ms.state.upper()}] {ms.title}{due}\n"
            f"    {bar} {ms.completion_pct}%  "
            f"({ms.closed_issues}/{ms.total_issues} issues closed)"
        )
    lines.append("")
    return "\n".join(lines)


def render_milestones_markdown(stats: List[MilestoneStat]) -> str:
    """Render milestone stats as a Markdown section."""
    if not stats:
        return "_No milestones found._\n"

    lines: List[str] = ["## Milestones", ""]
    header = "| # | Title | State | Progress | Closed / Total | Due |"
    sep    = "|---|-------|-------|----------|----------------|-----|"
    lines += [header, sep]

    for ms in stats:
        due = ms.due_on or "—"
        bar = _progress_bar(ms.completion_pct, width=10)
        lines.append(
            f"| {ms.number} | {ms.title} | {ms.state} "
            f"| `{bar}` {ms.completion_pct}% "
            f"| {ms.closed_issues} / {ms.total_issues} "
            f"| {due} |"
        )
    lines.append("")
    return "\n".join(lines)
