"""Tests for repodigest.config."""

import os
import textwrap

import pytest

from repodigest.config import Config, load_config, DEFAULT_DAYS, DEFAULT_OUTPUT_FORMAT


# ---------------------------------------------------------------------------
# Config.validate
# ---------------------------------------------------------------------------

def _valid_config(**kwargs) -> Config:
    defaults = dict(token="ghp_abc", repo="owner/repo", days=7, output_format="text", cache_ttl=300)
    defaults.update(kwargs)
    return Config(**defaults)


def test_validate_passes_for_valid_config():
    assert _valid_config().validate() == []


def test_validate_missing_token():
    errors = _valid_config(token="").validate()
    assert any("token" in e.lower() for e in errors)


def test_validate_bad_repo_format():
    errors = _valid_config(repo="noslash").validate()
    assert any("owner/name" in e for e in errors)


def test_validate_days_out_of_range():
    assert _valid_config(days=0).validate()
    assert _valid_config(days=366).validate()
    assert _valid_config(days=1).validate() == []
    assert _valid_config(days=365).validate() == []


def test_validate_invalid_format():
    errors = _valid_config(output_format="xml").validate()
    assert any("output_format" in e for e in errors)


def test_validate_negative_cache_ttl():
    errors = _valid_config(cache_ttl=-1).validate()
    assert any("cache_ttl" in e for e in errors)


# ---------------------------------------------------------------------------
# load_config — from file
# ---------------------------------------------------------------------------

def test_load_config_from_yaml(tmp_path):
    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text(textwrap.dedent("""\
        token: ghp_test
        repo: alice/wonderland
        days: 14
        output_format: markdown
        cache_ttl: 60
        extra_labels:
          - bug
          - enhancement
    """))
    cfg = load_config(path=str(cfg_file))
    assert cfg.token == "ghp_test"
    assert cfg.repo == "alice/wonderland"
    assert cfg.days == 14
    assert cfg.output_format == "markdown"
    assert cfg.cache_ttl == 60
    assert cfg.extra_labels == ["bug", "enhancement"]


def test_load_config_defaults_when_file_missing(tmp_path):
    cfg = load_config(path=str(tmp_path / "nonexistent.yml"))
    assert cfg.days == DEFAULT_DAYS
    assert cfg.output_format == DEFAULT_OUTPUT_FORMAT


def test_load_config_env_overrides_file(tmp_path, monkeypatch):
    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text("token: file_token\nrepo: owner/repo\n")
    monkeypatch.setenv("GITHUB_TOKEN", "env_token")
    monkeypatch.setenv("REPODIGEST_DAYS", "3")
    cfg = load_config(path=str(cfg_file))
    assert cfg.token == "env_token"
    assert cfg.days == 3


def test_load_config_explicit_overrides(tmp_path):
    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text("token: base\nrepo: owner/repo\n")
    cfg = load_config(path=str(cfg_file), overrides={"output_format": "json", "days": 30})
    assert cfg.output_format == "json"
    assert cfg.days == 30


def test_load_config_none_overrides_ignored(tmp_path):
    cfg_file = tmp_path / "cfg.yml"
    cfg_file.write_text("token: t\nrepo: o/r\ndays: 5\n")
    cfg = load_config(path=str(cfg_file), overrides={"days": None})
    assert cfg.days == 5
