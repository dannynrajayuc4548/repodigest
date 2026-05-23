"""Retry logic with exponential backoff for GitHub API requests."""

import time
import logging
from functools import wraps
from typing import Callable, Tuple, Type

logger = logging.getLogger(__name__)

DEFAULT_RETRYABLE_STATUS_CODES = (429, 500, 502, 503, 504)
DEFAULT_MAX_RETRIES = 3
DEFAULT_BACKOFF_BASE = 2.0
DEFAULT_BACKOFF_MAX = 60.0


class RetryExhausted(Exception):
    """Raised when all retry attempts have been exhausted."""

    def __init__(self, attempts: int, last_exception: Exception):
        self.attempts = attempts
        self.last_exception = last_exception
        super().__init__(
            f"Request failed after {attempts} attempt(s): {last_exception}"
        )


class RetryConfig:
    """Configuration for retry behaviour."""

    def __init__(
        self,
        max_retries: int = DEFAULT_MAX_RETRIES,
        backoff_base: float = DEFAULT_BACKOFF_BASE,
        backoff_max: float = DEFAULT_BACKOFF_MAX,
        retryable_exceptions: Tuple[Type[Exception], ...] = (),
        retryable_status_codes: Tuple[int, ...] = DEFAULT_RETRYABLE_STATUS_CODES,
    ):
        self.max_retries = max_retries
        self.backoff_base = backoff_base
        self.backoff_max = backoff_max
        self.retryable_exceptions = retryable_exceptions
        self.retryable_status_codes = retryable_status_codes

    def backoff_delay(self, attempt: int) -> float:
        """Return the delay in seconds for the given attempt (0-indexed)."""
        delay = self.backoff_base ** attempt
        return min(delay, self.backoff_max)


def with_retry(config: RetryConfig | None = None, _sleep: Callable = time.sleep):
    """Decorator that retries a function according to *config*.

    The decorated function may raise ``requests.HTTPError``; if the response
    status code is in ``config.retryable_status_codes`` the call is retried.
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exc: Exception | None = None
            for attempt in range(config.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:  # noqa: BLE001
                    status_code = getattr(
                        getattr(exc, "response", None), "status_code", None
                    )
                    retryable = isinstance(
                        exc, config.retryable_exceptions
                    ) or status_code in config.retryable_status_codes

                    if not retryable or attempt == config.max_retries:
                        raise

                    last_exc = exc
                    delay = config.backoff_delay(attempt)
                    logger.warning(
                        "Attempt %d/%d failed (%s). Retrying in %.1fs…",
                        attempt + 1,
                        config.max_retries + 1,
                        exc,
                        delay,
                    )
                    _sleep(delay)

            raise RetryExhausted(config.max_retries + 1, last_exc)  # type: ignore[arg-type]

        return wrapper

    return decorator
