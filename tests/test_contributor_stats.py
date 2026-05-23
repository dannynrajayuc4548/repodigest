"""Tests for repodigest.contributor_stats."""
import pytest
from repodigest.contributor_stats import compute_contributor_stats, ContributorStat


def _commit(login: str) -> dict:
    return {"author": {"login": login}, "commit": {"author": {"name": login}}}


def _pr(login: str, merged: bool = False) -> dict:
    return {
        "user": {"login": login},
        "merged_at": "2024-01-10T00:00:00Z" if merged else None,
    }


def _detail(login: str, additions: int = 0, deletions: int = 0) -> dict:
    return {
        "author": {"login": login},
        "stats": {"additions": additions, "deletions": deletions},
    }


def test_empty_inputs_return_empty_list():
    result = compute_contributor_stats([], [])
    assert result == []


def test_commit_count_aggregated():
    commits = [_commit("alice"), _commit("alice"), _commit("bob")]
    result = compute_contributor_stats(commits, [])
    by_login = {s.login: s for s in result}
    assert by_login["alice"].commit_count == 2
    assert by_login["bob"].commit_count == 1


def test_sorted_by_commit_count_descending():
    commits = [_commit("bob"), _commit("alice"), _commit("alice")]
    result = compute_contributor_stats(commits, [])
    assert result[0].login == "alice"
    assert result[1].login == "bob"


def test_pr_counts():
    prs = [_pr("alice", merged=True), _pr("alice", merged=False), _pr("bob", merged=True)]
    result = compute_contributor_stats([], prs)
    by_login = {s.login: s for s in result}
    assert by_login["alice"].prs_opened == 2
    assert by_login["alice"].prs_merged == 1
    assert by_login["bob"].prs_merged == 1


def test_diff_details_aggregated():
    details = [
        _detail("alice", additions=50, deletions=10),
        _detail("alice", additions=20, deletions=5),
        _detail("bob", additions=100, deletions=30),
    ]
    result = compute_contributor_stats([], [], diff_details=details)
    by_login = {s.login: s for s in result}
    assert by_login["alice"].lines_added == 70
    assert by_login["alice"].lines_deleted == 15
    assert by_login["alice"].total_changes == 85
    assert by_login["bob"].lines_added == 100


def test_to_dict_contains_expected_keys():
    stat = ContributorStat(login="alice", commit_count=3, prs_opened=1, prs_merged=1,
                           lines_added=40, lines_deleted=10)
    d = stat.to_dict()
    assert d["login"] == "alice"
    assert d["total_changes"] == 50
    assert "commit_count" in d
    assert "prs_opened" in d


def test_missing_author_login_falls_back_to_name():
    commit = {"author": None, "commit": {"author": {"name": "ghost"}}}
    result = compute_contributor_stats([commit], [])
    assert result[0].login == "ghost"


def test_combined_commits_and_prs():
    commits = [_commit("carol"), _commit("carol")]
    prs = [_pr("carol", merged=True)]
    result = compute_contributor_stats(commits, prs)
    assert len(result) == 1
    assert result[0].commit_count == 2
    assert result[0].prs_merged == 1
