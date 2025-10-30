"""
Tests for retry utilities.
"""

import pytest
import time
import asyncio
from unittest.mock import Mock

from decomposition_pipeline.errors.exceptions import (
    NetworkError,
    LLMError,
    RateLimitError,
    ValidationError,
)
from decomposition_pipeline.utils.retry import (
    exponential_backoff,
    should_retry_exception,
    retry,
    async_retry,
    RetryConfig,
    retry_on_network_error,
    retry_on_llm_error,
)


class TestExponentialBackoff:
    """Tests for exponential_backoff function."""

    def test_exponential_growth(self):
        """Test exponential growth of delay."""
        delays = [exponential_backoff(i, base_delay=1.0, jitter=False) for i in range(5)]

        assert delays[0] == 1.0  # 2^0 * 1.0
        assert delays[1] == 2.0  # 2^1 * 1.0
        assert delays[2] == 4.0  # 2^2 * 1.0
        assert delays[3] == 8.0  # 2^3 * 1.0
        assert delays[4] == 16.0  # 2^4 * 1.0

    def test_max_delay_limit(self):
        """Test max delay limit is enforced."""
        delay = exponential_backoff(10, base_delay=1.0, max_delay=10.0, jitter=False)
        assert delay == 10.0

    def test_jitter_variation(self):
        """Test jitter adds variation to delay."""
        delays = [exponential_backoff(1, base_delay=2.0, jitter=True) for _ in range(10)]

        # All delays should be within ±25% of base (2.0)
        for delay in delays:
            assert 1.5 <= delay <= 2.5

        # Delays should not all be the same (with very high probability)
        assert len(set(delays)) > 1


class TestShouldRetryException:
    """Tests for should_retry_exception function."""

    def test_retryable_network_error(self):
        """Test network error is retryable."""
        error = NetworkError("Connection failed")
        assert should_retry_exception(error, (NetworkError, LLMError))

    def test_retryable_llm_error(self):
        """Test LLM error is retryable."""
        error = LLMError("API call failed")
        assert should_retry_exception(error, (NetworkError, LLMError))

    def test_non_retryable_validation_error(self):
        """Test validation error is not retryable by default."""
        error = ValidationError("Invalid input")
        assert not should_retry_exception(error, (NetworkError, LLMError))

    def test_retryable_with_custom_exceptions(self):
        """Test custom retryable exceptions."""
        error = ValidationError("Invalid input")
        assert should_retry_exception(error, (ValidationError,))


class TestRetryDecorator:
    """Tests for retry decorator."""

    def test_successful_first_attempt(self):
        """Test function succeeds on first attempt."""
        mock_func = Mock(return_value="success")
        decorated = retry(max_attempts=3)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_on_retryable_error(self):
        """Test retry on retryable error."""
        mock_func = Mock(side_effect=[NetworkError("Failed"), NetworkError("Failed"), "success"])
        decorated = retry(max_attempts=3, base_delay=0.01)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_max_attempts_reached(self):
        """Test exception raised when max attempts reached."""
        mock_func = Mock(side_effect=NetworkError("Failed"))
        decorated = retry(max_attempts=3, base_delay=0.01)(mock_func)

        with pytest.raises(NetworkError):
            decorated()

        assert mock_func.call_count == 3

    def test_non_retryable_error_not_retried(self):
        """Test non-retryable error is not retried."""
        mock_func = Mock(side_effect=ValidationError("Invalid input"))
        decorated = retry(max_attempts=3)(mock_func)

        with pytest.raises(ValidationError):
            decorated()

        assert mock_func.call_count == 1

    def test_retry_with_custom_exceptions(self):
        """Test retry with custom retryable exceptions."""
        mock_func = Mock(side_effect=[ValidationError("Invalid"), "success"])
        decorated = retry(
            max_attempts=3,
            base_delay=0.01,
            retryable_exceptions=(ValidationError,),
        )(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_callback(self):
        """Test on_retry callback is called."""
        callback = Mock()
        mock_func = Mock(side_effect=[NetworkError("Failed"), "success"])
        decorated = retry(max_attempts=3, base_delay=0.01, on_retry=callback)(mock_func)

        result = decorated()

        assert result == "success"
        assert callback.call_count == 1
        assert isinstance(callback.call_args[0][0], NetworkError)
        assert callback.call_args[0][1] == 0  # First attempt (0-indexed)


@pytest.mark.asyncio
class TestAsyncRetryDecorator:
    """Tests for async_retry decorator."""

    async def test_async_successful_first_attempt(self):
        """Test async function succeeds on first attempt."""
        async def async_func():
            return "success"

        decorated = async_retry(max_attempts=3)(async_func)
        result = await decorated()

        assert result == "success"

    async def test_async_retry_on_error(self):
        """Test async retry on retryable error."""
        call_count = 0

        async def async_func():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise NetworkError("Failed")
            return "success"

        decorated = async_retry(max_attempts=3, base_delay=0.01)(async_func)
        result = await decorated()

        assert result == "success"
        assert call_count == 3

    async def test_async_max_attempts_reached(self):
        """Test async exception raised when max attempts reached."""
        async def async_func():
            raise NetworkError("Failed")

        decorated = async_retry(max_attempts=3, base_delay=0.01)(async_func)

        with pytest.raises(NetworkError):
            await decorated()

    async def test_async_with_delay(self):
        """Test async retry respects delay."""
        call_times = []

        async def async_func():
            call_times.append(time.time())
            if len(call_times) < 2:
                raise NetworkError("Failed")
            return "success"

        decorated = async_retry(max_attempts=3, base_delay=0.1, jitter=False)(async_func)
        await decorated()

        # Check that there was a delay between calls
        if len(call_times) >= 2:
            time_diff = call_times[1] - call_times[0]
            assert time_diff >= 0.1


class TestRetryConfig:
    """Tests for RetryConfig class."""

    def test_default_config(self):
        """Test default retry configuration."""
        config = RetryConfig()

        assert config.max_attempts == 3
        assert config.base_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential is True
        assert config.jitter is True
        assert NetworkError in config.retryable_exceptions
        assert LLMError in config.retryable_exceptions

    def test_custom_config(self):
        """Test custom retry configuration."""
        config = RetryConfig(
            max_attempts=5,
            base_delay=2.0,
            max_delay=30.0,
            exponential=False,
            jitter=False,
            retryable_exceptions=(ValidationError,),
        )

        assert config.max_attempts == 5
        assert config.base_delay == 2.0
        assert config.max_delay == 30.0
        assert config.exponential is False
        assert config.jitter is False
        assert config.retryable_exceptions == (ValidationError,)


class TestPreConfiguredRetryDecorators:
    """Tests for pre-configured retry decorators."""

    def test_retry_on_network_error(self):
        """Test retry_on_network_error decorator."""
        mock_func = Mock(side_effect=[NetworkError("Failed"), "success"])
        decorated = retry_on_network_error(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_on_llm_error(self):
        """Test retry_on_llm_error decorator."""
        mock_func = Mock(side_effect=[RateLimitError(), "success"])
        decorated = retry_on_llm_error(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 2


class TestRetryIntegration:
    """Integration tests for retry functionality."""

    def test_retry_with_exponential_backoff(self):
        """Test retry with exponential backoff timing."""
        call_times = []

        def timed_func():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise NetworkError("Failed")
            return "success"

        decorated = retry(max_attempts=3, base_delay=0.1, jitter=False)(timed_func)
        result = decorated()

        assert result == "success"
        assert len(call_times) == 3

        # Verify exponential backoff delays
        if len(call_times) >= 3:
            delay1 = call_times[1] - call_times[0]
            delay2 = call_times[2] - call_times[1]

            # Second delay should be roughly 2x first delay
            assert 0.08 <= delay1 <= 0.12  # ~0.1s
            assert 0.16 <= delay2 <= 0.24  # ~0.2s

    def test_mixed_error_types(self):
        """Test handling mixed error types."""
        errors = [
            NetworkError("Network failed"),
            LLMError("LLM failed"),
            RateLimitError(),
            "success",
        ]
        mock_func = Mock(side_effect=errors)
        decorated = retry(max_attempts=5, base_delay=0.01)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 4
