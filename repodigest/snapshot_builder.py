"""Build a DigestSnapshot from a Digest instance."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import TYPE_CHECKING

from repodigest.snapshot import DigestSnapshot

if TYPE_CHECKING:
    from repodigest.digest import Digest


def _week_start_iso() -> str:
    """Return the ISO-8601 date string for the start of the current UTC week (Monday)."""
    today = datetime.now(timezone.utc).date()
    monday = today - __import__("datetime").timedelta(days=today.weekday())
    return monday.isoformat()


def build_snapshot(repo: str, digest: "Digest", week_start: str | None = None) -> DigestSnapshot:
    """Convert a Digest into a persistable DigestSnapshot.

    Args:
        repo: Full repository slug, e.g. ``owner/name``.
        digest: Populated :class:`~repodigest.digest.Digest` instance.
        week_start: Optional ISO-8601 date string; defaults to current week's Monday.

    Returns:
        A :class:`DigestSnapshot` ready to be saved.
    """
    if week_start is None:
        week_start = _week_start_iso()

    top_contributors = [
        author for author, _ in digest.top_contributors()
    ]

    return DigestSnapshot(
        repo=repo,
        week_start=week_start,
        commit_count=digest.commit_count(),
        open_prs=digest.open_prs(),
        merged_prs=digest.merged_prs(),
        open_issues=digest.open_issues(),
        closed_issues=digest.closed_issues(),
        top_contributors=top_contributors,
        release_count=digest.release_count(),
    )
