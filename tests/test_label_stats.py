"""Tests for repodigest.label_stats."""
import pytest
from repodigest.label_stats import compute_label_stats, LabelStat, _extract_label_names


def _make_item(*label_names: str) -> dict:
    """Build a minimal PR/issue dict with the given labels."""
    return {"labels": [{"name": n} for n in label_names]}


# ---------------------------------------------------------------------------
# _extract_label_names
# ---------------------------------------------------------------------------

def test_extract_label_names_empty():
    assert _extract_label_names({}) == []


def test_extract_label_names_none_labels():
    assert _extract_label_names({"labels": None}) == []


def test_extract_label_names_returns_names():
    item = _make_item("bug", "enhancement")
    assert _extract_label_names(item) == ["bug", "enhancement"]


# ---------------------------------------------------------------------------
# compute_label_stats
# ---------------------------------------------------------------------------

def test_empty_inputs_return_empty_list():
    result = compute_label_stats([], [])
    assert result == []


def test_single_pr_label():
    prs = [_make_item("bug")]
    result = compute_label_stats(prs, [])
    assert len(result) == 1
    stat = result[0]
    assert stat.name == "bug"
    assert stat.count == 1
    assert stat.pr_count == 1
    assert stat.issue_count == 0


def test_single_issue_label():
    issues = [_make_item("docs")]
    result = compute_label_stats([], issues)
    assert result[0].issue_count == 1
    assert result[0].pr_count == 0


def test_label_counts_aggregated_across_prs_and_issues():
    prs = [_make_item("bug"), _make_item("bug", "enhancement")]
    issues = [_make_item("bug")]
    result = compute_label_stats(prs, issues)
    bug_stat = next(s for s in result if s.name == "bug")
    assert bug_stat.count == 3
    assert bug_stat.pr_count == 2
    assert bug_stat.issue_count == 1


def test_results_sorted_by_count_descending():
    prs = [_make_item("a"), _make_item("a"), _make_item("b")]
    result = compute_label_stats(prs, [])
    assert result[0].name == "a"
    assert result[1].name == "b"


def test_top_n_limits_results():
    prs = [_make_item("x", "y", "z")]
    result = compute_label_stats(prs, [], top_n=2)
    assert len(result) == 2


def test_to_dict_keys():
    stat = LabelStat(name="bug", count=3, pr_count=2, issue_count=1)
    d = stat.to_dict()
    assert set(d.keys()) == {"name", "count", "pr_count", "issue_count"}
    assert d["name"] == "bug"
    assert d["count"] == 3


def test_items_without_labels_field_ignored():
    prs = [{}, {"labels": []}]
    result = compute_label_stats(prs, [])
    assert result == []
