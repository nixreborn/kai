"""Cache decorators for endpoint optimization."""

import hashlib
import json
from collections.abc import Callable
from functools import wraps
from typing import Any

from fastapi import Request

from .redis_client import RedisCache


def cache_response(
    key_builder: Callable[[Request, dict[str, Any]], str],
    ttl: int,
) -> Callable[..., Any]:
    """
    Decorator to cache endpoint responses in Redis.

    Args:
        key_builder: Function that builds cache key from request and kwargs
        ttl: Time to live in seconds

    Returns:
        Decorator function

    Example:
        @cache_response(
            key_builder=lambda req, kwargs: f"user:{kwargs['user_id']}:profile",
            ttl=3600
        )
        async def get_user_profile(user_id: str, cache: RedisCache = Depends(get_redis)):
            ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Extract cache dependency from kwargs
            cache: RedisCache | None = kwargs.get("cache")

            if not cache:
                # No cache available, execute function directly
                return await func(*args, **kwargs)

            # Extract request if available
            request: Request | None = kwargs.get("request")

            # Build cache key
            try:
                cache_key = key_builder(request, kwargs)
            except Exception:
                # If key building fails, execute without caching
                return await func(*args, **kwargs)

            # Try to get from cache
            cached_data = await cache.get_json(cache_key)
            if cached_data is not None:
                return cached_data

            # Execute function and cache result
            result = await func(*args, **kwargs)

            # Cache the result
            await cache.set_json(cache_key, result, ttl=ttl)

            return result

        return wrapper

    return decorator


def hash_message(message: str) -> str:
    """
    Create a hash of a message for cache key generation.

    Args:
        message: Message to hash

    Returns:
        SHA256 hash of the message (first 16 characters)
    """
    return hashlib.sha256(message.encode()).hexdigest()[:16]


def invalidate_cache_pattern(pattern: str) -> Callable[..., Any]:
    """
    Decorator to invalidate cache entries matching a pattern after function execution.

    Args:
        pattern: Cache key pattern to invalidate (e.g., "user:123:*")

    Returns:
        Decorator function

    Example:
        @invalidate_cache_pattern("journal:list:{user_id}:*")
        async def create_journal_entry(user_id: str, cache: RedisCache = Depends(get_redis)):
            ...
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Execute function first
            result = await func(*args, **kwargs)

            # Extract cache dependency
            cache: RedisCache | None = kwargs.get("cache")

            if cache:
                # Format pattern with kwargs
                try:
                    formatted_pattern = pattern.format(**kwargs)
                    await cache.delete_pattern(formatted_pattern)
                except Exception:
                    # If invalidation fails, continue (already executed function)
                    pass

            return result

        return wrapper

    return decorator


def build_list_cache_key(
    resource: str,
    user_id: str,
    page: int = 1,
    page_size: int = 20,
    **filters: Any,
) -> str:
    """
    Build a standardized cache key for list endpoints.

    Args:
        resource: Resource name (e.g., "journal", "conversation")
        user_id: User identifier
        page: Page number
        page_size: Items per page
        **filters: Additional filter parameters

    Returns:
        Cache key string
    """
    key = f"{resource}:list:{user_id}:page:{page}:size:{page_size}"

    if filters:
        # Sort filters for consistent key generation
        sorted_filters = sorted(filters.items())
        filter_str = json.dumps(sorted_filters, sort_keys=True)
        filter_hash = hashlib.md5(filter_str.encode()).hexdigest()[:8]
        key += f":filters:{filter_hash}"

    return key
