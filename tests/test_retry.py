"""Tests for repodigest.retry."""

import pytest
from unittest.mock import MagicMock, patch

from repodigest.retry import RetryConfig, RetryExhausted, with_retry


# ---------------------------------------------------------------------------
# RetryConfig helpers
# ---------------------------------------------------------------------------

def test_backoff_delay_increases_exponentially():
    cfg = RetryConfig(backoff_base=2.0, backoff_max=60.0)
    assert cfg.backoff_delay(0) == 1.0
    assert cfg.backoff_delay(1) == 2.0
    assert cfg.backoff_delay(2) == 4.0


def test_backoff_delay_capped_at_max():
    cfg = RetryConfig(backoff_base=2.0, backoff_max=5.0)
    assert cfg.backoff_delay(10) == 5.0


# ---------------------------------------------------------------------------
# with_retry decorator — success path
# ---------------------------------------------------------------------------

def test_no_retry_on_success():
    sleep_mock = MagicMock()
    call_count = 0

    @with_retry(_sleep=sleep_mock)
    def always_succeeds():
        nonlocal call_count
        call_count += 1
        return "ok"

    result = always_succeeds()
    assert result == "ok"
    assert call_count == 1
    sleep_mock.assert_not_called()


# ---------------------------------------------------------------------------
# with_retry decorator — retry path
# ---------------------------------------------------------------------------

def _http_error_with_status(status_code: int):
    """Build a fake requests.HTTPError with a .response.status_code."""
    exc = Exception(f"HTTP {status_code}")
    exc.response = MagicMock(status_code=status_code)  # type: ignore[attr-defined]
    return exc


def test_retries_on_retryable_status_code():
    sleep_mock = MagicMock()
    attempts = 0

    @with_retry(RetryConfig(max_retries=2), _sleep=sleep_mock)
    def flaky():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise _http_error_with_status(503)
        return "done"

    assert flaky() == "done"
    assert attempts == 3
    assert sleep_mock.call_count == 2


def test_raises_immediately_on_non_retryable_status():
    sleep_mock = MagicMock()

    @with_retry(RetryConfig(max_retries=3), _sleep=sleep_mock)
    def bad_request():
        raise _http_error_with_status(400)

    with pytest.raises(Exception, match="HTTP 400"):
        bad_request()

    sleep_mock.assert_not_called()


def test_raises_after_max_retries_exhausted():
    sleep_mock = MagicMock()
    cfg = RetryConfig(max_retries=2)

    @with_retry(cfg, _sleep=sleep_mock)
    def always_fails():
        raise _http_error_with_status(500)

    with pytest.raises(Exception):
        always_fails()

    assert sleep_mock.call_count == 2


def test_retry_exhausted_message():
    exc = RetryExhausted(3, ValueError("boom"))
    assert "3" in str(exc)
    assert "boom" in str(exc)


def test_default_config_used_when_none_provided():
    sleep_mock = MagicMock()
    calls = 0

    @with_retry(_sleep=sleep_mock)
    def intermittent():
        nonlocal calls
        calls += 1
        if calls == 1:
            raise _http_error_with_status(429)
        return "ok"

    assert intermittent() == "ok"
    assert calls == 2
