"""Aggregate diff statistics (additions, deletions, changed files) for a digest period."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Dict


@dataclass
class FileStat:
    filename: str
    additions: int
    deletions: int
    changes: int


@dataclass
class DiffStats:
    total_additions: int = 0
    total_deletions: int = 0
    total_changes: int = 0
    changed_files: int = 0
    top_files: List[FileStat] = field(default_factory=list)

    @property
    def churn(self) -> int:
        """Total lines touched (additions + deletions)."""
        return self.total_additions + self.total_deletions


def _parse_file_stat(raw: Dict) -> FileStat:
    return FileStat(
        filename=raw.get("filename", ""),
        additions=raw.get("additions", 0),
        deletions=raw.get("deletions", 0),
        changes=raw.get("changes", 0),
    )


def compute_diff_stats(commit_details: List[Dict], top_n: int = 5) -> DiffStats:
    """Compute aggregate diff statistics from a list of detailed commit payloads.

    Each element of *commit_details* should be the JSON response from
    ``GET /repos/{owner}/{repo}/commits/{sha}`` which includes a ``stats``
    object and a ``files`` list.
    """
    total_additions = 0
    total_deletions = 0
    total_changes = 0
    file_map: Dict[str, FileStat] = {}

    for detail in commit_details:
        stats = detail.get("stats", {})
        total_additions += stats.get("additions", 0)
        total_deletions += stats.get("deletions", 0)
        total_changes += stats.get("total", 0)

        for raw_file in detail.get("files", []):
            name = raw_file.get("filename", "")
            if name in file_map:
                existing = file_map[name]
                file_map[name] = FileStat(
                    filename=name,
                    additions=existing.additions + raw_file.get("additions", 0),
                    deletions=existing.deletions + raw_file.get("deletions", 0),
                    changes=existing.changes + raw_file.get("changes", 0),
                )
            else:
                file_map[name] = _parse_file_stat(raw_file)

    top_files = sorted(file_map.values(), key=lambda f: f.changes, reverse=True)[:top_n]

    return DiffStats(
        total_additions=total_additions,
        total_deletions=total_deletions,
        total_changes=total_changes,
        changed_files=len(file_map),
        top_files=top_files,
    )
