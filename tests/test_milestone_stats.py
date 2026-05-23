"""Tests for repodigest.milestone_stats."""
import pytest
from repodigest.milestone_stats import (
    MilestoneStat,
    compute_milestone_stats,
    _parse_milestone,
)


def _make_raw(
    title="v1.0",
    number=1,
    state="open",
    open_issues=3,
    closed_issues=7,
    due_on=None,
) -> dict:
    return {
        "title": title,
        "number": number,
        "state": state,
        "open_issues": open_issues,
        "closed_issues": closed_issues,
        "due_on": due_on,
    }


def test_parse_milestone_fields():
    raw = _make_raw(title="Beta", number=5, state="closed", open_issues=0, closed_issues=10, due_on="2024-06-01T00:00:00Z")
    ms = _parse_milestone(raw)
    assert ms.title == "Beta"
    assert ms.number == 5
    assert ms.state == "closed"
    assert ms.open_issues == 0
    assert ms.closed_issues == 10
    assert ms.due_on == "2024-06-01T00:00:00Z"


def test_completion_pct_no_issues():
    ms = MilestoneStat(title="Empty", number=1, state="open", open_issues=0, closed_issues=0, due_on=None)
    assert ms.completion_pct == 0.0


def test_completion_pct_partial():
    ms = MilestoneStat(title="Half", number=2, state="open", open_issues=5, closed_issues=5, due_on=None)
    assert ms.completion_pct == 50.0


def test_completion_pct_full():
    ms = MilestoneStat(title="Done", number=3, state="closed", open_issues=0, closed_issues=20, due_on=None)
    assert ms.completion_pct == 100.0


def test_total_issues():
    ms = MilestoneStat(title="T", number=1, state="open", open_issues=4, closed_issues=6, due_on=None)
    assert ms.total_issues == 10


def test_to_dict_keys():
    ms = MilestoneStat(title="v2", number=2, state="open", open_issues=2, closed_issues=8, due_on=None)
    d = ms.to_dict()
    assert set(d.keys()) == {"title", "number", "state", "open_issues", "closed_issues", "due_on", "completion_pct"}
    assert d["completion_pct"] == 80.0


def test_compute_empty_list():
    assert compute_milestone_stats([]) == []


def test_compute_state_filter_open():
    raws = [
        _make_raw(title="A", number=1, state="open"),
        _make_raw(title="B", number=2, state="closed"),
        _make_raw(title="C", number=3, state="open"),
    ]
    result = compute_milestone_stats(raws, state_filter="open")
    assert all(s.state == "open" for s in result)
    assert len(result) == 2


def test_compute_state_filter_closed():
    raws = [
        _make_raw(title="A", number=1, state="open"),
        _make_raw(title="B", number=2, state="closed"),
    ]
    result = compute_milestone_stats(raws, state_filter="closed")
    assert len(result) == 1
    assert result[0].title == "B"


def test_compute_sort_open_first():
    raws = [
        _make_raw(title="Closed", number=1, state="closed"),
        _make_raw(title="Open", number=2, state="open"),
    ]
    result = compute_milestone_stats(raws)
    assert result[0].state == "open"
    assert result[1].state == "closed"


def test_compute_sort_by_number_within_state():
    raws = [
        _make_raw(title="B", number=3, state="open"),
        _make_raw(title="A", number=1, state="open"),
        _make_raw(title="C", number=2, state="open"),
    ]
    result = compute_milestone_stats(raws)
    numbers = [s.number for s in result]
    assert numbers == [1, 2, 3]
