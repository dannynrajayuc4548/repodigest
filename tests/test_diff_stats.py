"""Tests for repodigest.diff_stats and repodigest.github_diff_fetcher."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from repodigest.diff_stats import compute_diff_stats, DiffStats
from repodigest.github_diff_fetcher import fetch_commit_details, diff_stats_for_repo


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_detail(additions: int, deletions: int, files=None) -> dict:
    return {
        "stats": {"additions": additions, "deletions": deletions, "total": additions + deletions},
        "files": files or [],
    }


def _make_file(filename: str, additions: int, deletions: int) -> dict:
    return {
        "filename": filename,
        "additions": additions,
        "deletions": deletions,
        "changes": additions + deletions,
    }


# ---------------------------------------------------------------------------
# compute_diff_stats
# ---------------------------------------------------------------------------

def test_empty_details_returns_zero_stats():
    stats = compute_diff_stats([])
    assert stats.total_additions == 0
    assert stats.total_deletions == 0
    assert stats.churn == 0
    assert stats.changed_files == 0
    assert stats.top_files == []


def test_single_commit_aggregated():
    detail = _make_detail(10, 5, files=[_make_file("foo.py", 10, 5)])
    stats = compute_diff_stats([detail])
    assert stats.total_additions == 10
    assert stats.total_deletions == 5
    assert stats.churn == 15
    assert stats.changed_files == 1


def test_multiple_commits_summed():
    details = [
        _make_detail(3, 1, files=[_make_file("a.py", 3, 1)]),
        _make_detail(7, 2, files=[_make_file("b.py", 7, 2)]),
    ]
    stats = compute_diff_stats(details)
    assert stats.total_additions == 10
    assert stats.total_deletions == 3
    assert stats.changed_files == 2


def test_same_file_across_commits_merged():
    details = [
        _make_detail(5, 0, files=[_make_file("shared.py", 5, 0)]),
        _make_detail(3, 1, files=[_make_file("shared.py", 3, 1)]),
    ]
    stats = compute_diff_stats(details)
    assert stats.changed_files == 1
    assert stats.top_files[0].filename == "shared.py"
    assert stats.top_files[0].additions == 8


def test_top_files_limited_to_top_n():
    files = [_make_file(f"file{i}.py", i, 0) for i in range(10)]
    detail = _make_detail(45, 0, files=files)
    stats = compute_diff_stats([detail], top_n=3)
    assert len(stats.top_files) == 3
    # highest changes should be first
    assert stats.top_files[0].changes >= stats.top_files[1].changes


# ---------------------------------------------------------------------------
# fetch_commit_details / diff_stats_for_repo
# ---------------------------------------------------------------------------

def test_fetch_commit_details_calls_client():
    client = MagicMock()
    client._get.return_value = {"sha": "abc", "stats": {}, "files": []}
    results = fetch_commit_details(client, "owner/repo", ["abc", "def"])
    assert len(results) == 2
    assert client._get.call_count == 2


def test_fetch_skips_on_exception():
    client = MagicMock()
    client._get.side_effect = [Exception("network error"), {"sha": "def", "stats": {}, "files": []}]
    results = fetch_commit_details(client, "owner/repo", ["abc", "def"])
    assert len(results) == 1


def test_max_commits_respected():
    client = MagicMock()
    client._get.return_value = {"stats": {}, "files": []}
    shas = [f"sha{i}" for i in range(20)]
    fetch_commit_details(client, "owner/repo", shas, max_commits=5)
    assert client._get.call_count == 5


def test_diff_stats_for_repo_extracts_shas():
    client = MagicMock()
    client._get.return_value = {"stats": {}, "files": []}
    commits = [{"sha": "aaa"}, {"sha": "bbb"}]
    results = diff_stats_for_repo(client, "owner/repo", commits)
    assert len(results) == 2
