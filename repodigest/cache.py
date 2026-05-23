"""Simple file-based cache for GitHub API responses."""

import json
import os
import time
from pathlib import Path
from typing import Any, Optional

DEFAULT_CACHE_DIR = Path.home() / ".cache" / "repodigest"
DEFAULT_TTL = 3600  # 1 hour in seconds


class Cache:
    """File-based JSON cache with TTL support."""

    def __init__(self, cache_dir: Path = DEFAULT_CACHE_DIR, ttl: int = DEFAULT_TTL):
        self.cache_dir = Path(cache_dir)
        self.ttl = ttl
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _cache_path(self, key: str) -> Path:
        safe_key = key.replace("/", "_").replace("?", "_").replace("&", "_")
        return self.cache_dir / f"{safe_key}.json"

    def get(self, key: str) -> Optional[Any]:
        """Return cached value if present and not expired, else None."""
        path = self._cache_path(key)
        if not path.exists():
            return None
        try:
            with path.open("r") as f:
                entry = json.load(f)
            if time.time() - entry["timestamp"] > self.ttl:
                path.unlink(missing_ok=True)
                return None
            return entry["data"]
        except (json.JSONDecodeError, KeyError, OSError):
            return None

    def set(self, key: str, value: Any) -> None:
        """Store value in cache with current timestamp."""
        path = self._cache_path(key)
        entry = {"timestamp": time.time(), "data": value}
        try:
            with path.open("w") as f:
                json.dump(entry, f)
        except OSError:
            pass  # Cache write failures are non-fatal

    def clear(self, key: Optional[str] = None) -> None:
        """Remove a specific key or all cached entries."""
        if key:
            self._cache_path(key).unlink(missing_ok=True)
        else:
            for f in self.cache_dir.glob("*.json"):
                f.unlink(missing_ok=True)

    def size(self) -> int:
        """Return the number of cached entries."""
        return len(list(self.cache_dir.glob("*.json")))
