"""Tests for the file-based cache module."""

import json
import time
from pathlib import Path

import pytest

from repodigest.cache import Cache


@pytest.fixture
def cache(tmp_path):
    return Cache(cache_dir=tmp_path / "cache", ttl=60)


def test_cache_miss_on_empty(cache):
    assert cache.get("some/key") is None


def test_cache_set_and_get(cache):
    cache.set("repos/owner/repo", {"stars": 42})
    result = cache.get("repos/owner/repo")
    assert result == {"stars": 42}


def test_cache_returns_none_after_ttl(tmp_path):
    short_cache = Cache(cache_dir=tmp_path / "cache", ttl=1)
    short_cache.set("key", "value")
    time.sleep(1.1)
    assert short_cache.get("key") is None


def test_cache_clear_specific_key(cache):
    cache.set("key1", "a")
    cache.set("key2", "b")
    cache.clear("key1")
    assert cache.get("key1") is None
    assert cache.get("key2") == "b"


def test_cache_clear_all(cache):
    cache.set("key1", "a")
    cache.set("key2", "b")
    cache.clear()
    assert cache.size() == 0


def test_cache_size(cache):
    assert cache.size() == 0
    cache.set("k1", 1)
    cache.set("k2", 2)
    assert cache.size() == 2


def test_cache_handles_corrupt_file(cache, tmp_path):
    cache_dir = tmp_path / "cache"
    corrupt = cache_dir / "bad_key.json"
    corrupt.write_text("not valid json")
    assert cache.get("bad_key") is None


def test_cache_key_with_special_chars(cache):
    key = "repos/owner/repo?since=2024-01-01&per_page=100"
    cache.set(key, ["commit1", "commit2"])
    assert cache.get(key) == ["commit1", "commit2"]
