"""Integration tests for filtered_digest."""
import pytest
from unittest.mock import MagicMock
from datetime import datetime, timezone

from repodigest.digest import Digest
from repodigest.filters import FilterConfig
from repodigest.digest_with_filters import filtered_digest, build_filter_config_from_cli


def _make_digest():
    def _commit(login):
        return {"author": {"login": login}, "stats": {"additions": 5, "deletions": 2}}

    def _pr(login, labels=None):
        return {
            "user": {"login": login},
            "labels": [{"name": l} for l in (labels or [])],
        }

    def _issue(login, labels=None):
        return {
            "user": {"login": login},
            "labels": [{"name": l} for l in (labels or [])],
        }

    return Digest(
        repo="owner/repo",
        since=datetime(2024, 1, 1, tzinfo=timezone.utc),
        commits=[
            _commit("alice"),
            _commit("dependabot[bot]"),
            _commit("bob"),
        ],
        open_prs=[_pr("alice", ["bug"]), _pr("renovate-bot")],
        merged_prs=[_pr("bob", ["enhancement"])],
        open_issues=[_issue("alice"), _issue("ghost-bot")],
        closed_issues=[_issue("bob")],
        releases=[],
    )


def test_default_filter_removes_bots():
    digest = _make_digest()
    result = filtered_digest(digest)
    logins = [c["author"]["login"] for c in result.commits]
    assert "dependabot[bot]" not in logins
    assert "alice" in logins


def test_author_filter_restricts_commits():
    digest = _make_digest()
    fc = FilterConfig(authors=["alice"])
    result = filtered_digest(digest, fc)
    assert all(c["author"]["login"] == "alice" for c in result.commits)


def test_label_filter_restricts_prs():
    digest = _make_digest()
    fc = FilterConfig(labels=["bug"])
    result = filtered_digest(digest, fc)
    assert len(result.open_prs) == 1
    assert result.open_prs[0]["user"]["login"] == "alice"


def test_releases_are_never_filtered():
    digest = _make_digest()
    digest.releases.append({"tag_name": "v1.0"})
    fc = FilterConfig(authors=["alice"])
    result = filtered_digest(digest, fc)
    assert result.releases == [{"tag_name": "v1.0"}]


def test_build_filter_config_from_cli_defaults():
    fc = build_filter_config_from_cli()
    assert fc.authors == []
    assert fc.labels == []
    assert fc.exclude_bots is True
    assert fc.min_additions is None


def test_build_filter_config_from_cli_custom():
    fc = build_filter_config_from_cli(
        authors=["alice"],
        labels=["bug"],
        exclude_bots=False,
        min_additions=10,
    )
    assert fc.authors == ["alice"]
    assert fc.labels == ["bug"]
    assert fc.exclude_bots is False
    assert fc.min_additions == 10
