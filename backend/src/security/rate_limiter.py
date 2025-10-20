"""Rate limiting configuration for Kai backend using SlowAPI."""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def rate_limit_key_func(request: Request) -> str:
    """
    Generate rate limit key based on client IP and user authentication.

    For authenticated users, use user ID for more accurate rate limiting.
    For anonymous users, use IP address.

    Args:
        request: FastAPI request object

    Returns:
        Rate limit key (user ID or IP address)
    """
    # Try to get user from request state (set by auth middleware)
    user = getattr(request.state, "user", None)

    if user and hasattr(user, "id"):
        # Use user ID for authenticated requests
        return f"user:{user.id}"

    # Fall back to IP address for anonymous requests
    return f"ip:{get_remote_address(request)}"


# Initialize rate limiter with Redis backend for production
# For development, uses in-memory storage
limiter = Limiter(
    key_func=rate_limit_key_func,
    default_limits=["100 per minute"],
    headers_enabled=True,
    storage_uri="memory://",  # Change to redis:// in production
)


# Rate limit configurations for different endpoint types
class RateLimits:
    """Rate limit configurations for different endpoints."""

    # Authentication endpoints
    LOGIN = "5 per minute"
    REGISTER = "3 per minute"
    REFRESH = "10 per minute"
    PASSWORD_RESET = "3 per hour"

    # Chat endpoints
    CHAT_MESSAGE = "30 per minute"
    PROACTIVE_CHECK_IN = "10 per minute"

    # Journal endpoints
    JOURNAL_CREATE = "20 per minute"
    JOURNAL_READ = "60 per minute"
    JOURNAL_UPDATE = "20 per minute"
    JOURNAL_DELETE = "10 per minute"

    # Profile endpoints
    PROFILE_READ = "60 per minute"
    PROFILE_UPDATE = "10 per minute"

    # Admin endpoints
    ADMIN_OPERATIONS = "30 per minute"


def configure_rate_limiter_for_production(redis_url: str) -> Limiter:
    """
    Configure rate limiter with Redis backend for production use.

    Args:
        redis_url: Redis connection URL (e.g., redis://localhost:6379)

    Returns:
        Configured Limiter instance
    """
    return Limiter(
        key_func=rate_limit_key_func,
        default_limits=["100 per minute"],
        headers_enabled=True,
        storage_uri=redis_url,
        retry_after="http-date",
    )


def get_rate_limit_headers() -> dict[str, str]:
    """
    Get standard rate limit headers to include in responses.

    Returns:
        Dictionary of rate limit headers
    """
    return {
        "X-RateLimit-Limit": "Rate limit maximum",
        "X-RateLimit-Remaining": "Rate limit remaining",
        "X-RateLimit-Reset": "Rate limit reset time",
    }
