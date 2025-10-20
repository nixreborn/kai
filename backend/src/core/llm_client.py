"""OpenAI-compatible LLM client configuration with retry and circuit breaker support."""

import asyncio
import logging
import time
from typing import Any

from openai import APIConnectionError, APIError, APITimeoutError, AsyncOpenAI
from pydantic_ai.models.openai import OpenAIChatModel
from pydantic_ai.providers import Provider

from .config import settings

logger = logging.getLogger(__name__)


class CircuitBreaker:
    """Circuit breaker pattern for LLM failures."""

    def __init__(self, failure_threshold: int = 5, timeout: float = 60.0):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            timeout: Time in seconds before attempting to close circuit
        """
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.failure_count = 0
        self.last_failure_time: float | None = None
        self.state = "closed"  # closed, open, half_open

    def record_success(self) -> None:
        """Record a successful call."""
        self.failure_count = 0
        self.state = "closed"
        self.last_failure_time = None

    def record_failure(self) -> None:
        """Record a failed call."""
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.failure_count >= self.failure_threshold:
            self.state = "open"
            logger.warning(
                f"Circuit breaker opened after {self.failure_count} failures"
            )

    def can_attempt(self) -> bool:
        """Check if a call can be attempted."""
        if self.state == "closed":
            return True

        if self.state == "open":
            if self.last_failure_time is None:
                return True

            time_since_failure = time.time() - self.last_failure_time
            if time_since_failure >= self.timeout:
                self.state = "half_open"
                logger.info("Circuit breaker entering half-open state")
                return True
            return False

        # half_open state - allow single attempt
        return True

    def reset(self) -> None:
        """Reset the circuit breaker."""
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "closed"


# Global circuit breaker instance
_circuit_breaker = CircuitBreaker(
    failure_threshold=settings.llm_circuit_breaker_threshold,
    timeout=settings.llm_circuit_breaker_timeout,
)


class CustomOpenAIProvider(Provider[AsyncOpenAI]):
    """Custom OpenAI provider with custom base URL and connection pooling."""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        timeout: float = 30.0,
        max_retries: int = 3,
    ) -> None:
        """
        Initialize the provider.

        Args:
            base_url: Base URL for the LLM service
            api_key: API key for authentication
            timeout: Request timeout in seconds
            max_retries: Maximum number of retries on failure
        """
        self._client = AsyncOpenAI(
            base_url=base_url,
            api_key=api_key,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._base_url = base_url
        self._timeout = timeout
        self._max_retries = max_retries

    @property
    def client(self) -> AsyncOpenAI:
        """Get the client."""
        return self._client

    @property
    def base_url(self) -> str:
        """Get the base URL."""
        return self._base_url

    @property
    def name(self) -> str:
        """Get the provider name."""
        return "custom-openai"


async def retry_with_backoff(
    func: Any,
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
) -> Any:
    """
    Retry a function with exponential backoff.

    Args:
        func: Async function to retry
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay between retries in seconds
        backoff_factor: Multiplier for delay on each retry

    Returns:
        Result of the function call

    Raises:
        Last exception if all retries fail
    """
    delay = initial_delay
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            # Check circuit breaker before attempting
            if not _circuit_breaker.can_attempt():
                raise APIConnectionError(
                    "Circuit breaker is open - too many recent failures"
                )

            result = await func()
            _circuit_breaker.record_success()
            return result

        except (APITimeoutError, APIConnectionError, APIError) as e:
            last_exception = e
            _circuit_breaker.record_failure()

            if attempt == max_retries:
                logger.error(
                    f"All {max_retries} retry attempts failed: {e}",
                    exc_info=True,
                )
                break

            logger.warning(
                f"Attempt {attempt + 1}/{max_retries + 1} failed: {e}. "
                f"Retrying in {delay}s..."
            )
            await asyncio.sleep(delay)
            delay *= backoff_factor

    raise last_exception or Exception("All retries failed")


def get_llm_model(model_name: str | None = None) -> OpenAIChatModel:
    """
    Get an OpenAI-compatible model instance with retry and timeout support.

    Args:
        model_name: Optional specific model name to use. Defaults to settings.llm_model.

    Returns:
        OpenAIChatModel configured for the local LLM endpoint.
    """
    # Create custom provider with timeout and retry settings
    provider = CustomOpenAIProvider(
        base_url=settings.llm_base_url,
        api_key=settings.llm_api_key,
        timeout=settings.llm_timeout,
        max_retries=settings.llm_max_retries,
    )

    # Return OpenAI model with the custom provider
    return OpenAIChatModel(
        model_name=model_name or settings.llm_model,
        provider=provider,
    )


def get_circuit_breaker() -> CircuitBreaker:
    """Get the global circuit breaker instance."""
    return _circuit_breaker


async def check_llm_health() -> dict[str, Any]:
    """
    Check LLM service health.

    Returns:
        Dictionary with health status and details
    """
    try:
        client = AsyncOpenAI(
            base_url=settings.llm_base_url,
            api_key=settings.llm_api_key,
            timeout=5.0,  # Short timeout for health check
        )

        start_time = time.time()

        # Try to list models as a health check
        models = await client.models.list()

        latency = time.time() - start_time

        return {
            "status": "healthy",
            "latency_ms": round(latency * 1000, 2),
            "models_available": len(models.data) if hasattr(models, 'data') else 0,
            "circuit_breaker_state": _circuit_breaker.state,
            "circuit_breaker_failures": _circuit_breaker.failure_count,
        }

    except APITimeoutError:
        return {
            "status": "unhealthy",
            "error": "Connection timeout",
            "circuit_breaker_state": _circuit_breaker.state,
        }
    except APIConnectionError as e:
        return {
            "status": "unhealthy",
            "error": f"Connection error: {str(e)}",
            "circuit_breaker_state": _circuit_breaker.state,
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": f"Unexpected error: {str(e)}",
            "circuit_breaker_state": _circuit_breaker.state,
        }
