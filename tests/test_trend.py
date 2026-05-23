"""Tests for repodigest.trend."""

from unittest.mock import MagicMock

import pytest

from repodigest.trend import (
    TrendSnapshot,
    TrendDelta,
    compute_trend,
    snapshot_from_digest,
)


def _snap(commits=10, prs=3, issues=5, contributors=2) -> TrendSnapshot:
    return TrendSnapshot(
        commit_count=commits,
        merged_prs=prs,
        open_issues=issues,
        new_contributors=contributors,
    )


# ---------------------------------------------------------------------------
# compute_trend
# ---------------------------------------------------------------------------

def test_compute_trend_returns_none_without_previous():
    assert compute_trend(_snap(), previous=None) is None


def test_compute_trend_positive_deltas():
    prev = _snap(commits=5, prs=1, issues=3, contributors=1)
    curr = _snap(commits=10, prs=3, issues=5, contributors=2)
    delta = compute_trend(curr, prev)
    assert delta is not None
    assert delta.commit_delta == 5
    assert delta.merged_pr_delta == 2
    assert delta.open_issue_delta == 2
    assert delta.contributor_delta == 1


def test_compute_trend_negative_deltas():
    prev = _snap(commits=20, prs=8, issues=10, contributors=4)
    curr = _snap(commits=10, prs=3, issues=5, contributors=2)
    delta = compute_trend(curr, prev)
    assert delta.commit_delta == -10
    assert delta.merged_pr_delta == -5


def test_compute_trend_zero_deltas():
    snap = _snap()
    delta = compute_trend(snap, snap)
    assert delta.commit_delta == 0
    assert delta.merged_pr_delta == 0


# ---------------------------------------------------------------------------
# TrendDelta helpers
# ---------------------------------------------------------------------------

def test_direction_up():
    delta = TrendDelta(commit_delta=3, merged_pr_delta=1, open_issue_delta=2, contributor_delta=1)
    assert delta.commit_direction() == "up"
    assert delta.pr_direction() == "up"


def test_direction_down():
    delta = TrendDelta(commit_delta=-1, merged_pr_delta=-2, open_issue_delta=-3, contributor_delta=-1)
    assert delta.commit_direction() == "down"
    assert delta.issue_direction() == "down"


def test_direction_unchanged():
    delta = TrendDelta(commit_delta=0, merged_pr_delta=0, open_issue_delta=0, contributor_delta=0)
    assert delta.commit_direction() == "unchanged"


def test_summary_contains_labels():
    delta = TrendDelta(commit_delta=5, merged_pr_delta=-2, open_issue_delta=0, contributor_delta=1)
    summary = delta.summary()
    assert "Commits" in summary
    assert "Merged PRs" in summary
    assert "Open issues" in summary
    assert "Contributors" in summary
    assert "+5" in summary
    assert "-2" in summary


# ---------------------------------------------------------------------------
# snapshot_from_digest
# ---------------------------------------------------------------------------

def test_snapshot_from_digest():
    digest = MagicMock()
    digest.commit_count = 15
    digest.merged_prs = 4
    digest.open_issues = 7
    digest.top_contributors = ["alice", "bob", "carol"]

    snap = snapshot_from_digest(digest)
    assert snap.commit_count == 15
    assert snap.merged_prs == 4
    assert snap.open_issues == 7
    assert snap.new_contributors == 3
