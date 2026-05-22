"""Tests for digest building and formatting."""

from datetime import datetime, timezone
from unittest.mock import MagicMock

import pytest

from repodigest.digest import Digest, build_digest
from repodigest.formatter import format_digest

SINCE = datetime(2024, 1, 1, tzinfo=timezone.utc)


def _make_commit(sha: str, message: str, author: str = "Alice") -> dict:
    return {"sha": sha, "commit": {"message": message, "author": {"name": author}}}


def _make_pr(number: int, title: str, state: str = "open", merged: bool = False) -> dict:
    return {"number": number, "title": title, "state": state, "merged_at": "2024-01-02" if merged else None}


def _make_issue(number: int, title: str, state: str = "open") -> dict:
    return {"number": number, "title": title, "state": state}


def _make_release(tag: str, name: str) -> dict:
    return {"tag_name": tag, "name": name, "published_at": "2024-01-05T10:00:00Z"}


@pytest.fixture()
def mock_client() -> MagicMock:
    client = MagicMock()
    client.get_commits.return_value = [_make_commit("abc1234", "feat: add thing")]
    client.get_pull_requests.return_value = [
        _make_pr(1, "Add feature", state="closed", merged=True),
        _make_pr(2, "Fix bug", state="open"),
    ]
    client.get_issues.return_value = [
        _make_issue(10, "Something broken", state="closed"),
        _make_issue(11, "New request"),
    ]
    client.get_releases.return_value = [_make_release("v1.2.0", "Release 1.2.0")]
    return client


def test_build_digest_populates_fields(mock_client: MagicMock) -> None:
    digest = build_digest("owner", "repo", mock_client, since=SINCE)
    assert digest.commit_count == 1
    assert len(digest.merged_prs) == 1
    assert len(digest.open_prs) == 1
    assert len(digest.closed_issues) == 1
    assert len(digest.open_issues) == 1
    assert digest.latest_release is not None
    assert digest.latest_release["tag_name"] == "v1.2.0"


def test_digest_no_releases() -> None:
    digest = Digest(owner="o", repo="r", since=SINCE)
    assert digest.latest_release is None


def test_format_digest_contains_key_info(mock_client: MagicMock) -> None:
    digest = build_digest("owner", "repo", mock_client, since=SINCE)
    output = format_digest(digest)
    assert "owner/repo" in output
    assert "abc1234"[:7] in output
    assert "Add feature" in output
    assert "v1.2.0" in output
    assert "Something broken" in output
