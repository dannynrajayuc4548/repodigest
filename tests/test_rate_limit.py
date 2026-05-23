"""Tests for rate limit parsing and status reporting."""

from datetime import datetime, timezone, timedelta
from unittest.mock import MagicMock

import pytest

from repodigest.rate_limit import (
    RateLimitStatus,
    parse_rate_limit,
    check_rate_limit,
)


def _make_reset_ts(offset_seconds: int = 3600) -> int:
    future = datetime.now(timezone.utc) + timedelta(seconds=offset_seconds)
    return int(future.timestamp())


def _make_rate_limit_payload(limit=5000, remaining=4200, used=800, offset=3600):
    reset = _make_reset_ts(offset)
    return {
        "resources": {
            "core": {
                "limit": limit,
                "remaining": remaining,
                "used": used,
                "reset": reset,
            }
        }
    }


def test_parse_rate_limit_basic():
    data = _make_rate_limit_payload()
    status = parse_rate_limit(data)
    assert status.limit == 5000
    assert status.remaining == 4200
    assert status.used == 800
    assert isinstance(status.reset_at, datetime)


def test_percent_remaining():
    data = _make_rate_limit_payload(limit=1000, remaining=250)
    status = parse_rate_limit(data)
    assert status.percent_remaining == pytest.approx(25.0)


def test_is_exhausted_false():
    data = _make_rate_limit_payload(remaining=10)
    status = parse_rate_limit(data)
    assert not status.is_exhausted


def test_is_exhausted_true():
    data = _make_rate_limit_payload(remaining=0)
    status = parse_rate_limit(data)
    assert status.is_exhausted


def test_reset_in_seconds_positive():
    data = _make_rate_limit_payload(offset=120)
    status = parse_rate_limit(data)
    assert 100 <= status.reset_in_seconds <= 130


def test_reset_in_seconds_past():
    data = _make_rate_limit_payload(offset=-60)
    status = parse_rate_limit(data)
    assert status.reset_in_seconds == 0


def test_str_representation():
    data = _make_rate_limit_payload(limit=5000, remaining=4200)
    status = parse_rate_limit(data)
    result = str(status)
    assert "4200/5000" in result
    assert "84.0%" in result


def test_check_rate_limit_success():
    mock_client = MagicMock()
    mock_client._get.return_value = _make_rate_limit_payload()
    status = check_rate_limit(mock_client)
    assert status is not None
    assert status.limit == 5000
    mock_client._get.assert_called_once_with("/rate_limit")


def test_check_rate_limit_returns_none_on_error():
    mock_client = MagicMock()
    mock_client._get.side_effect = Exception("network error")
    status = check_rate_limit(mock_client)
    assert status is None
