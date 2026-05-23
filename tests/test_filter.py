"""Tests for repodigest.filter module."""
import pytest
from repodigest.filter import FilterConfig, filter_commits, filter_prs, filter_issues


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _commit(login: str, message: str = "fix: something") -> dict:
    return {"author": {"login": login}, "commit": {"message": message}}


def _pr(
    login: str,
    title: str = "Add feature",
    labels: list | None = None,
    comments: int = 0,
) -> dict:
    return {
        "user": {"login": login},
        "title": title,
        "labels": [{"name": l} for l in (labels or [])],
        "comments": comments,
    }


def _issue(
    login: str,
    title: str = "Bug report",
    labels: list | None = None,
    comments: int = 0,
) -> dict:
    return {
        "user": {"login": login},
        "title": title,
        "labels": [{"name": l} for l in (labels or [])],
        "comments": comments,
    }


# ---------------------------------------------------------------------------
# FilterConfig defaults
# ---------------------------------------------------------------------------

def test_filter_config_defaults():
    cfg = FilterConfig()
    assert cfg.authors == []
    assert cfg.labels == []
    assert cfg.exclude_bots is False
    assert cfg.min_comments == 0
    assert cfg.title_contains is None


# ---------------------------------------------------------------------------
# filter_commits
# ---------------------------------------------------------------------------

def test_filter_commits_no_criteria_returns_all():
    commits = [_commit("alice"), _commit("bob")]
    assert filter_commits(commits, FilterConfig()) == commits


def test_filter_commits_by_author():
    commits = [_commit("alice"), _commit("bob")]
    result = filter_commits(commits, FilterConfig(authors=["alice"]))
    assert len(result) == 1 and result[0]["author"]["login"] == "alice"


def test_filter_commits_exclude_bots():
    commits = [_commit("alice"), _commit("dependabot[bot]"), _commit("renovate-bot")]
    result = filter_commits(commits, FilterConfig(exclude_bots=True))
    assert len(result) == 1


def test_filter_commits_title_contains():
    commits = [_commit("alice", "fix: typo"), _commit("bob", "feat: new endpoint")]
    result = filter_commits(commits, FilterConfig(title_contains="feat"))
    assert len(result) == 1 and "feat" in result[0]["commit"]["message"]


# ---------------------------------------------------------------------------
# filter_prs
# ---------------------------------------------------------------------------

def test_filter_prs_by_label():
    prs = [_pr("alice", labels=["bug"]), _pr("bob", labels=["enhancement"])]
    result = filter_prs(prs, FilterConfig(labels=["bug"]))
    assert len(result) == 1


def test_filter_prs_min_comments():
    prs = [_pr("alice", comments=0), _pr("bob", comments=3)]
    result = filter_prs(prs, FilterConfig(min_comments=2))
    assert len(result) == 1 and result[0]["user"]["login"] == "bob"


def test_filter_prs_title_contains_case_insensitive():
    prs = [_pr("alice", title="Fix Typo"), _pr("bob", title="Add Tests")]
    result = filter_prs(prs, FilterConfig(title_contains="fix"))
    assert len(result) == 1


# ---------------------------------------------------------------------------
# filter_issues
# ---------------------------------------------------------------------------

def test_filter_issues_exclude_bots():
    issues = [_issue("alice"), _issue("github-actions[bot]")]
    result = filter_issues(issues, FilterConfig(exclude_bots=True))
    assert len(result) == 1 and result[0]["user"]["login"] == "alice"


def test_filter_issues_multiple_criteria():
    issues = [
        _issue("alice", title="Critical bug", labels=["bug"], comments=5),
        _issue("bob", title="Minor tweak", labels=["enhancement"], comments=1),
        _issue("carol", title="Another bug", labels=["bug"], comments=0),
    ]
    cfg = FilterConfig(labels=["bug"], min_comments=3)
    result = filter_issues(issues, cfg)
    assert len(result) == 1 and result[0]["user"]["login"] == "alice"
