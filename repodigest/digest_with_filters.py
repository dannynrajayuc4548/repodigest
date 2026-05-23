"""Thin wrapper that applies FilterConfig to a Digest before rendering."""
from __future__ import annotations

from typing import Optional

from repodigest.digest import Digest
from repodigest.filters import FilterConfig, apply_filters


def filtered_digest(digest: Digest, fc: Optional[FilterConfig] = None) -> Digest:
    """Return a *new* Digest whose lists have been narrowed by *fc*.

    If *fc* is None a default :class:`FilterConfig` is used, which only
    strips bot accounts.
    """
    if fc is None:
        fc = FilterConfig()

    filtered = Digest(
        repo=digest.repo,
        since=digest.since,
        commits=apply_filters(digest.commits, fc.match_commit),
        open_prs=apply_filters(digest.open_prs, fc.match_pr),
        merged_prs=apply_filters(digest.merged_prs, fc.match_pr),
        open_issues=apply_filters(digest.open_issues, fc.match_issue),
        closed_issues=apply_filters(digest.closed_issues, fc.match_issue),
        releases=digest.releases,  # releases are not filtered by author/label
    )
    return filtered


def build_filter_config_from_cli(
    authors: Optional[list] = None,
    labels: Optional[list] = None,
    exclude_bots: bool = True,
    min_additions: Optional[int] = None,
    min_deletions: Optional[int] = None,
) -> FilterConfig:
    """Convenience factory used by the CLI layer."""
    return FilterConfig(
        authors=authors or [],
        labels=labels or [],
        exclude_bots=exclude_bots,
        min_additions=min_additions,
        min_deletions=min_deletions,
    )
