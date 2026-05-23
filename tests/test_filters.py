"""Tests for repodigest.filters."""
import pytest
from repodigest.filters import FilterConfig, apply_filters


def _commit(login="alice", additions=10, deletions=5):
    return {
        "author": {"login": login},
        "stats": {"additions": additions, "deletions": deletions},
    }


def _pr(login="alice", labels=None):
    return {
        "user": {"login": login},
        "labels": [{"name": lbl} for lbl in (labels or [])],
    }


def _issue(login="alice", labels=None):
    return {
        "user": {"login": login},
        "labels": [{"name": lbl} for lbl in (labels or [])],
    }


# ---------------------------------------------------------------------------
# is_bot
# ---------------------------------------------------------------------------

def test_is_bot_detects_bracket_bot():
    fc = FilterConfig()
    assert fc.is_bot("dependabot[bot]") is True


def test_is_bot_detects_suffix_bot():
    fc = FilterConfig()
    assert fc.is_bot("renovate-bot") is True


def test_is_bot_returns_false_for_human():
    fc = FilterConfig()
    assert fc.is_bot("alice") is False


# ---------------------------------------------------------------------------
# match_commit
# ---------------------------------------------------------------------------

def test_commit_excluded_when_bot_and_exclude_bots_true():
    fc = FilterConfig(exclude_bots=True)
    assert fc.match_commit(_commit(login="dependabot[bot]")) is False


def test_commit_included_when_bot_but_exclude_bots_false():
    fc = FilterConfig(exclude_bots=False)
    assert fc.match_commit(_commit(login="dependabot[bot]")) is True


def test_commit_author_filter():
    fc = FilterConfig(authors=["alice"])
    assert fc.match_commit(_commit(login="alice")) is True
    assert fc.match_commit(_commit(login="bob")) is False


def test_commit_min_additions_filter():
    fc = FilterConfig(min_additions=20)
    assert fc.match_commit(_commit(additions=25)) is True
    assert fc.match_commit(_commit(additions=5)) is False


def test_commit_min_deletions_filter():
    fc = FilterConfig(min_deletions=10)
    assert fc.match_commit(_commit(deletions=15)) is True
    assert fc.match_commit(_commit(deletions=3)) is False


# ---------------------------------------------------------------------------
# match_pr / match_issue
# ---------------------------------------------------------------------------

def test_pr_label_filter_matches():
    fc = FilterConfig(labels=["bug"])
    assert fc.match_pr(_pr(labels=["bug", "help wanted"])) is True


def test_pr_label_filter_excludes():
    fc = FilterConfig(labels=["bug"])
    assert fc.match_pr(_pr(labels=["enhancement"])) is False


def test_issue_no_label_filter_passes_all():
    fc = FilterConfig()
    assert fc.match_issue(_issue(labels=["anything"])) is True


# ---------------------------------------------------------------------------
# apply_filters helper
# ---------------------------------------------------------------------------

def test_apply_filters_returns_subset():
    fc = FilterConfig(authors=["alice"])
    commits = [_commit("alice"), _commit("bob"), _commit("alice")]
    result = apply_filters(commits, fc.match_commit)
    assert len(result) == 2
    assert all(c["author"]["login"] == "alice" for c in result)


def test_apply_filters_empty_list():
    fc = FilterConfig()
    assert apply_filters([], fc.match_commit) == []
