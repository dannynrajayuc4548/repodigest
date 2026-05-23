"""GitHub API rate limit tracking and reporting."""

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional


@dataclass
class RateLimitStatus:
    limit: int
    remaining: int
    reset_at: datetime
    used: int

    @property
    def reset_in_seconds(self) -> int:
        now = datetime.now(timezone.utc)
        delta = self.reset_at - now
        return max(0, int(delta.total_seconds()))

    @property
    def percent_remaining(self) -> float:
        if self.limit == 0:
            return 0.0
        return (self.remaining / self.limit) * 100

    @property
    def is_exhausted(self) -> bool:
        return self.remaining == 0

    def __str__(self) -> str:
        return (
            f"Rate limit: {self.remaining}/{self.limit} remaining "
            f"({self.percent_remaining:.1f}%), "
            f"resets in {self.reset_in_seconds}s"
        )


def parse_rate_limit(data: dict) -> RateLimitStatus:
    """Parse rate limit info from GitHub API response data."""
    core = data.get("resources", {}).get("core", data.get("rate", {}))
    reset_ts = core.get("reset", 0)
    reset_at = datetime.fromtimestamp(reset_ts, tz=timezone.utc)
    return RateLimitStatus(
        limit=core.get("limit", 0),
        remaining=core.get("remaining", 0),
        reset_at=reset_at,
        used=core.get("used", 0),
    )


def check_rate_limit(client) -> Optional[RateLimitStatus]:
    """Fetch and return the current rate limit status from GitHub."""
    try:
        data = client._get("/rate_limit")
        return parse_rate_limit(data)
    except Exception:
        return None
