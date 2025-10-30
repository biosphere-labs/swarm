"""
Retry utilities for handling transient failures.

Provides decorators and utilities for implementing retry logic
with exponential backoff for LLM calls and external APIs.
"""

import asyncio
import functools
import logging
import random
import time
from typing import Any, Callable, Optional, Tuple, Type, TypeVar, Union

from decomposition_pipeline.errors import (
    NetworkError,
    LLMError,
    RateLimitError,
    TimeoutError,
)

logger = logging.getLogger(__name__)

T = TypeVar("T")


def exponential_backoff(
    attempt: int,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    jitter: bool = True,
) -> float:
    """
    Calculate exponential backoff delay with optional jitter.

    Args:
        attempt: Current retry attempt (0-indexed)
        base_delay: Base delay in seconds
        max_delay: Maximum delay in seconds
        jitter: Whether to add random jitter

    Returns:
        Delay in seconds
    """
    delay = min(base_delay * (2 ** attempt), max_delay)

    if jitter:
        # Add random jitter (±25%)
        jitter_amount = delay * 0.25
        delay = delay + random.uniform(-jitter_amount, jitter_amount)

    return max(0, delay)


def should_retry_exception(
    exc: Exception,
    retryable_exceptions: Tuple[Type[Exception], ...],
) -> bool:
    """
    Determine if an exception should trigger a retry.

    Args:
        exc: Exception instance
        retryable_exceptions: Tuple of exception types that should be retried

    Returns:
        True if should retry, False otherwise
    """
    return isinstance(exc, retryable_exceptions)


def retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential: bool = True,
    jitter: bool = True,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    Decorator for retrying functions with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including initial)
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries
        exponential: Whether to use exponential backoff
        jitter: Whether to add random jitter to delays
        retryable_exceptions: Tuple of exceptions that should trigger retry
        on_retry: Optional callback called before each retry

    Returns:
        Decorated function

    Example:
        ```python
        @retry(max_attempts=3, base_delay=2.0)
        def call_llm_api():
            # API call that might fail
            pass
        ```
    """
    if retryable_exceptions is None:
        retryable_exceptions = (NetworkError, LLMError, RateLimitError, TimeoutError)

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc

                    # Check if we should retry this exception
                    if not should_retry_exception(exc, retryable_exceptions):
                        raise

                    # Don't retry if this was the last attempt
                    if attempt >= max_attempts - 1:
                        raise

                    # Calculate delay
                    if exponential:
                        delay = exponential_backoff(
                            attempt, base_delay, max_delay, jitter
                        )
                    else:
                        delay = base_delay

                    # Log retry attempt
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed: {exc}. "
                        f"Retrying in {delay:.2f}s...",
                        extra={
                            "attempt": attempt + 1,
                            "max_attempts": max_attempts,
                            "delay": delay,
                            "exception": str(exc),
                        },
                    )

                    # Call on_retry callback if provided
                    if on_retry:
                        try:
                            on_retry(exc, attempt)
                        except Exception as callback_exc:
                            logger.error(
                                f"on_retry callback failed: {callback_exc}",
                                exc_info=True,
                            )

                    # Wait before retrying
                    time.sleep(delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry logic failed unexpectedly")

        return wrapper

    return decorator


def async_retry(
    max_attempts: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential: bool = True,
    jitter: bool = True,
    retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    on_retry: Optional[Callable[[Exception, int], None]] = None,
):
    """
    Async decorator for retrying functions with exponential backoff.

    Args:
        max_attempts: Maximum number of attempts (including initial)
        base_delay: Base delay between retries in seconds
        max_delay: Maximum delay between retries
        exponential: Whether to use exponential backoff
        jitter: Whether to add random jitter to delays
        retryable_exceptions: Tuple of exceptions that should trigger retry
        on_retry: Optional callback called before each retry

    Returns:
        Decorated async function

    Example:
        ```python
        @async_retry(max_attempts=3, base_delay=2.0)
        async def call_llm_api():
            # Async API call that might fail
            pass
        ```
    """
    if retryable_exceptions is None:
        retryable_exceptions = (NetworkError, LLMError, RateLimitError, TimeoutError)

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    return await func(*args, **kwargs)
                except Exception as exc:
                    last_exception = exc

                    # Check if we should retry this exception
                    if not should_retry_exception(exc, retryable_exceptions):
                        raise

                    # Don't retry if this was the last attempt
                    if attempt >= max_attempts - 1:
                        raise

                    # Calculate delay
                    if exponential:
                        delay = exponential_backoff(
                            attempt, base_delay, max_delay, jitter
                        )
                    else:
                        delay = base_delay

                    # Log retry attempt
                    logger.warning(
                        f"Attempt {attempt + 1}/{max_attempts} failed: {exc}. "
                        f"Retrying in {delay:.2f}s...",
                        extra={
                            "attempt": attempt + 1,
                            "max_attempts": max_attempts,
                            "delay": delay,
                            "exception": str(exc),
                        },
                    )

                    # Call on_retry callback if provided
                    if on_retry:
                        try:
                            on_retry(exc, attempt)
                        except Exception as callback_exc:
                            logger.error(
                                f"on_retry callback failed: {callback_exc}",
                                exc_info=True,
                            )

                    # Wait before retrying
                    await asyncio.sleep(delay)

            # This should never be reached, but just in case
            if last_exception:
                raise last_exception
            raise RuntimeError("Retry logic failed unexpectedly")

        return wrapper

    return decorator


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential: bool = True,
        jitter: bool = True,
        retryable_exceptions: Optional[Tuple[Type[Exception], ...]] = None,
    ):
        """
        Initialize retry configuration.

        Args:
            max_attempts: Maximum number of attempts
            base_delay: Base delay between retries
            max_delay: Maximum delay between retries
            exponential: Use exponential backoff
            jitter: Add random jitter
            retryable_exceptions: Exceptions that trigger retry
        """
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential = exponential
        self.jitter = jitter
        self.retryable_exceptions = retryable_exceptions or (
            NetworkError,
            LLMError,
            RateLimitError,
            TimeoutError,
        )


class RetryContext:
    """Context manager for retry operations."""

    def __init__(self, config: RetryConfig):
        """
        Initialize retry context.

        Args:
            config: Retry configuration
        """
        self.config = config
        self.attempt = 0
        self.last_exception = None

    def __enter__(self):
        """Enter retry context."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit retry context."""
        if exc_type is None:
            return True

        self.last_exception = exc_val

        # Check if we should retry
        if not should_retry_exception(exc_val, self.config.retryable_exceptions):
            return False

        # Check if we have attempts left
        if self.attempt >= self.config.max_attempts - 1:
            return False

        # Calculate delay
        if self.config.exponential:
            delay = exponential_backoff(
                self.attempt,
                self.config.base_delay,
                self.config.max_delay,
                self.config.jitter,
            )
        else:
            delay = self.config.base_delay

        # Log and wait
        logger.warning(
            f"Attempt {self.attempt + 1}/{self.config.max_attempts} failed. "
            f"Retrying in {delay:.2f}s..."
        )
        time.sleep(delay)

        self.attempt += 1
        return True


# Pre-configured retry decorators for common use cases

retry_on_network_error = retry(
    max_attempts=3,
    base_delay=2.0,
    retryable_exceptions=(NetworkError, TimeoutError),
)

retry_on_llm_error = retry(
    max_attempts=5,
    base_delay=1.0,
    max_delay=30.0,
    retryable_exceptions=(LLMError, RateLimitError, TimeoutError),
)

async_retry_on_network_error = async_retry(
    max_attempts=3,
    base_delay=2.0,
    retryable_exceptions=(NetworkError, TimeoutError),
)

async_retry_on_llm_error = async_retry(
    max_attempts=5,
    base_delay=1.0,
    max_delay=30.0,
    retryable_exceptions=(LLMError, RateLimitError, TimeoutError),
)
