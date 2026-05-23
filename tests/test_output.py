"""Tests for repodigest.output — render and write_output helpers."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from io import StringIO
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from repodigest.digest import Digest
from repodigest.output import render, write_output, SUPPORTED_FORMATS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def digest() -> Digest:
    """Return a minimal Digest with predictable values."""
    client = MagicMock()
    client.get_commits.return_value = [{"author": {"login": "alice"}} for _ in range(3)]
    client.get_pull_requests.return_value = (
        [{"number": 1, "title": "Open PR", "user": {"login": "alice"}}],
        [{"number": 2, "title": "Merged PR", "user": {"login": "bob"}}],
    )
    client.get_issues.return_value = (
        [{"number": 10, "title": "Bug", "user": {"login": "charlie"}}],
        [{"number": 11, "title": "Fixed", "user": {"login": "alice"}}],
    )
    client.get_releases.return_value = [{"tag_name": "v1.0.0", "name": "First release"}]

    since = datetime(2024, 1, 1, tzinfo=timezone.utc)
    d = Digest(client=client, repo="owner/repo", since=since)
    return d


# ---------------------------------------------------------------------------
# render()
# ---------------------------------------------------------------------------

def test_render_text_returns_string(digest: Digest) -> None:
    result = render(digest, fmt="text")
    assert isinstance(result, str)
    assert len(result) > 0


def test_render_markdown_returns_string(digest: Digest) -> None:
    result = render(digest, fmt="markdown")
    assert isinstance(result, str)


def test_render_json_is_valid_json(digest: Digest) -> None:
    result = render(digest, fmt="json")
    data = json.loads(result)  # must not raise
    assert data["repo"] == "owner/repo"
    assert data["commit_count"] == 3
    assert data["open_prs"] == 1
    assert data["merged_prs"] == 1
    assert data["new_releases"] == 1


def test_render_json_contains_top_contributors(digest: Digest) -> None:
    data = json.loads(render(digest, fmt="json"))
    assert "top_contributors" in data
    assert data["top_contributors"][0][0] == "alice"


def test_render_unsupported_format_raises(digest: Digest) -> None:
    with pytest.raises(ValueError, match="Unsupported format"):
        render(digest, fmt="xml")


# ---------------------------------------------------------------------------
# write_output()
# ---------------------------------------------------------------------------

def test_write_output_to_stdout(digest: Digest, capsys) -> None:
    write_output(digest, fmt="text")
    captured = capsys.readouterr()
    assert len(captured.out) > 0


def test_write_output_to_file(digest: Digest, tmp_path: Path) -> None:
    out_file = tmp_path / "report.md"
    write_output(digest, fmt="markdown", output_path=str(out_file))
    assert out_file.exists()
    assert len(out_file.read_text()) > 0


def test_write_output_json_to_file(digest: Digest, tmp_path: Path) -> None:
    out_file = tmp_path / "report.json"
    write_output(digest, fmt="json", output_path=str(out_file))
    data = json.loads(out_file.read_text())
    assert data["repo"] == "owner/repo"


def test_write_output_creates_parent_dirs(digest: Digest, tmp_path: Path) -> None:
    out_file = tmp_path / "nested" / "dir" / "report.txt"
    write_output(digest, fmt="text", output_path=str(out_file))
    assert out_file.exists()
