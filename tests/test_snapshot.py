"""Tests for snapshot persistence and snapshot builder."""

from __future__ import annotations

import json
import os
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from repodigest.snapshot import (
    DigestSnapshot,
    list_snapshots,
    load_snapshot,
    save_snapshot,
)
from repodigest.snapshot_builder import build_snapshot


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_snapshot(**kwargs) -> DigestSnapshot:
    defaults = dict(
        repo="owner/repo",
        week_start="2024-01-01",
        commit_count=10,
        open_prs=3,
        merged_prs=5,
        open_issues=7,
        closed_issues=2,
        top_contributors=["alice", "bob"],
        release_count=1,
    )
    defaults.update(kwargs)
    return DigestSnapshot(**defaults)


@pytest.fixture(autouse=True)
def isolated_snapshot_dir(tmp_path, monkeypatch):
    monkeypatch.setenv("REPODIGEST_SNAPSHOT_DIR", str(tmp_path))
    yield tmp_path


# ---------------------------------------------------------------------------
# DigestSnapshot serialisation
# ---------------------------------------------------------------------------

def test_to_dict_round_trip():
    snap = _make_snapshot()
    assert DigestSnapshot.from_dict(snap.to_dict()) == snap


def test_save_creates_file(isolated_snapshot_dir):
    snap = _make_snapshot()
    path = save_snapshot(snap)
    assert path.exists()
    data = json.loads(path.read_text())
    assert data["commit_count"] == 10


def test_load_returns_none_for_missing():
    result = load_snapshot("owner/repo", "1999-01-01")
    assert result is None


def test_save_and_load_round_trip():
    snap = _make_snapshot()
    save_snapshot(snap)
    loaded = load_snapshot(snap.repo, snap.week_start)
    assert loaded == snap


def test_list_snapshots_returns_all(isolated_snapshot_dir):
    snaps = [
        _make_snapshot(week_start="2024-01-01"),
        _make_snapshot(week_start="2024-01-08"),
        _make_snapshot(week_start="2024-01-15"),
    ]
    for s in snaps:
        save_snapshot(s)
    result = list_snapshots("owner/repo")
    assert len(result) == 3


def test_list_snapshots_ignores_other_repos(isolated_snapshot_dir):
    save_snapshot(_make_snapshot(repo="owner/repo", week_start="2024-01-01"))
    save_snapshot(_make_snapshot(repo="other/repo", week_start="2024-01-01"))
    result = list_snapshots("owner/repo")
    assert len(result) == 1


# ---------------------------------------------------------------------------
# build_snapshot
# ---------------------------------------------------------------------------

def _make_digest_mock(commits=5, open_prs=2, merged_prs=3,
                      open_issues=4, closed_issues=1, releases=0):
    d = MagicMock()
    d.commit_count.return_value = commits
    d.open_prs.return_value = open_prs
    d.merged_prs.return_value = merged_prs
    d.open_issues.return_value = open_issues
    d.closed_issues.return_value = closed_issues
    d.release_count.return_value = releases
    d.top_contributors.return_value = [("alice", 3), ("bob", 2)]
    return d


def test_build_snapshot_fields():
    digest = _make_digest_mock()
    snap = build_snapshot("owner/repo", digest, week_start="2024-06-03")
    assert snap.repo == "owner/repo"
    assert snap.week_start == "2024-06-03"
    assert snap.commit_count == 5
    assert snap.top_contributors == ["alice", "bob"]


def test_build_snapshot_default_week_start():
    digest = _make_digest_mock()
    snap = build_snapshot("owner/repo", digest)
    # Should be a valid ISO date string
    from datetime import date
    date.fromisoformat(snap.week_start)
