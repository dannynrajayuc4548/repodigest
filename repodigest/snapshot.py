"""Persist and load weekly digest snapshots to disk for trend comparison."""

from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


@dataclass
class DigestSnapshot:
    repo: str
    week_start: str  # ISO-8601
    commit_count: int
    open_prs: int
    merged_prs: int
    open_issues: int
    closed_issues: int
    top_contributors: list[str]
    release_count: int

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "DigestSnapshot":
        return cls(
            repo=data["repo"],
            week_start=data["week_start"],
            commit_count=data["commit_count"],
            open_prs=data["open_prs"],
            merged_prs=data["merged_prs"],
            open_issues=data["open_issues"],
            closed_issues=data["closed_issues"],
            top_contributors=data.get("top_contributors", []),
            release_count=data.get("release_count", 0),
        )


def _snapshot_dir() -> Path:
    base = Path(os.environ.get("REPODIGEST_SNAPSHOT_DIR", Path.home() / ".repodigest" / "snapshots"))
    base.mkdir(parents=True, exist_ok=True)
    return base


def _snapshot_path(repo: str, week_start: str) -> Path:
    safe_repo = repo.replace("/", "__")
    return _snapshot_dir() / f"{safe_repo}__{week_start}.json"


def save_snapshot(snapshot: DigestSnapshot) -> Path:
    path = _snapshot_path(snapshot.repo, snapshot.week_start)
    path.write_text(json.dumps(snapshot.to_dict(), indent=2))
    return path


def load_snapshot(repo: str, week_start: str) -> Optional[DigestSnapshot]:
    path = _snapshot_path(repo, week_start)
    if not path.exists():
        return None
    data = json.loads(path.read_text())
    return DigestSnapshot.from_dict(data)


def list_snapshots(repo: str) -> list[DigestSnapshot]:
    safe_repo = repo.replace("/", "__")
    paths = sorted(_snapshot_dir().glob(f"{safe_repo}__*.json"))
    snapshots = []
    for p in paths:
        try:
            snapshots.append(DigestSnapshot.from_dict(json.loads(p.read_text())))
        except (KeyError, json.JSONDecodeError):
            continue
    return snapshots
