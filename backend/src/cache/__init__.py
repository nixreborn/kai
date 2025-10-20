"""Cache module for Redis-based caching."""

from .decorators import (
    build_list_cache_key,
    cache_response,
    hash_message,
    invalidate_cache_pattern,
)
from .redis_client import (
    TTL_AI_RESPONSE,
    TTL_CONVERSATION,
    TTL_JOURNAL_LIST,
    TTL_USER_PROFILE,
    RedisCache,
    build_ai_response_key,
    build_conversation_key,
    build_journal_list_key,
    build_user_profile_key,
    get_redis,
)

__all__ = [
    # Client and dependencies
    "RedisCache",
    "get_redis",
    # Key builders
    "build_user_profile_key",
    "build_journal_list_key",
    "build_ai_response_key",
    "build_conversation_key",
    "build_list_cache_key",
    # TTL constants
    "TTL_USER_PROFILE",
    "TTL_JOURNAL_LIST",
    "TTL_AI_RESPONSE",
    "TTL_CONVERSATION",
    # Decorators
    "cache_response",
    "invalidate_cache_pattern",
    "hash_message",
]
