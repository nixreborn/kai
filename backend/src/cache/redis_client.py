"""Redis client for caching."""

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

import redis.asyncio as redis
from pydantic import BaseModel

from ..core.config import settings

logger = logging.getLogger(__name__)


class RedisCache:
    """Redis cache client with async support."""

    def __init__(self, redis_client: redis.Redis) -> None:
        """
        Initialize Redis cache.

        Args:
            redis_client: Async Redis client instance
        """
        self.client = redis_client

    async def get(self, key: str) -> str | None:
        """
        Get value from cache.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found
        """
        try:
            value = await self.client.get(key)
            if value:
                logger.debug(f"Cache hit: {key}")
                return value.decode("utf-8") if isinstance(value, bytes) else value
            logger.debug(f"Cache miss: {key}")
            return None
        except Exception as e:
            logger.error(f"Redis get error for key {key}: {e}")
            return None

    async def set(
        self,
        key: str,
        value: str,
        ttl: int | None = None,
    ) -> bool:
        """
        Set value in cache.

        Args:
            key: Cache key
            value: Value to cache
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            if ttl:
                await self.client.setex(key, ttl, value)
            else:
                await self.client.set(key, value)
            logger.debug(f"Cache set: {key} (TTL: {ttl}s)")
            return True
        except Exception as e:
            logger.error(f"Redis set error for key {key}: {e}")
            return False

    async def get_json(self, key: str) -> dict[str, Any] | list[Any] | None:
        """
        Get JSON value from cache.

        Args:
            key: Cache key

        Returns:
            Deserialized JSON value or None if not found
        """
        value = await self.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error for key {key}: {e}")
                return None
        return None

    async def set_json(
        self,
        key: str,
        value: dict[str, Any] | list[Any] | BaseModel,
        ttl: int | None = None,
    ) -> bool:
        """
        Set JSON value in cache.

        Args:
            key: Cache key
            value: Value to serialize and cache (dict, list, or Pydantic model)
            ttl: Time to live in seconds (optional)

        Returns:
            True if successful, False otherwise
        """
        try:
            if isinstance(value, BaseModel):
                json_str = value.model_dump_json()
            else:
                json_str = json.dumps(value)
            return await self.set(key, json_str, ttl)
        except Exception as e:
            logger.error(f"JSON encode error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> bool:
        """
        Delete key from cache.

        Args:
            key: Cache key

        Returns:
            True if key was deleted, False otherwise
        """
        try:
            result = await self.client.delete(key)
            logger.debug(f"Cache delete: {key} (deleted: {result})")
            return bool(result)
        except Exception as e:
            logger.error(f"Redis delete error for key {key}: {e}")
            return False

    async def delete_pattern(self, pattern: str) -> int:
        """
        Delete all keys matching a pattern.

        Args:
            pattern: Pattern to match (e.g., "user:*")

        Returns:
            Number of keys deleted
        """
        try:
            cursor = 0
            deleted = 0
            while True:
                cursor, keys = await self.client.scan(cursor, match=pattern, count=100)
                if keys:
                    deleted += await self.client.delete(*keys)
                if cursor == 0:
                    break
            logger.info(f"Cache pattern delete: {pattern} ({deleted} keys)")
            return deleted
        except Exception as e:
            logger.error(f"Redis pattern delete error for pattern {pattern}: {e}")
            return 0

    async def exists(self, key: str) -> bool:
        """
        Check if key exists in cache.

        Args:
            key: Cache key

        Returns:
            True if key exists, False otherwise
        """
        try:
            result = await self.client.exists(key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis exists error for key {key}: {e}")
            return False

    async def ttl(self, key: str) -> int:
        """
        Get time to live for a key.

        Args:
            key: Cache key

        Returns:
            TTL in seconds, -1 if no expiry, -2 if key doesn't exist
        """
        try:
            return await self.client.ttl(key)
        except Exception as e:
            logger.error(f"Redis TTL error for key {key}: {e}")
            return -2

    async def ping(self) -> bool:
        """
        Check if Redis is available.

        Returns:
            True if Redis responds to ping, False otherwise
        """
        try:
            await self.client.ping()
            return True
        except Exception as e:
            logger.error(f"Redis ping failed: {e}")
            return False

    async def close(self) -> None:
        """Close Redis connection."""
        await self.client.aclose()


# Global Redis client
_redis_client: redis.Redis | None = None


async def get_redis_client() -> redis.Redis:
    """
    Get or create Redis client.

    Returns:
        Async Redis client instance
    """
    global _redis_client

    if _redis_client is None:
        redis_url = getattr(settings, "redis_url", "redis://localhost:6379/0")
        _redis_client = redis.from_url(
            redis_url,
            encoding="utf-8",
            decode_responses=False,
            max_connections=10,
        )
        logger.info(f"Redis client initialized: {redis_url}")

    return _redis_client


async def close_redis_client() -> None:
    """Close Redis client connection."""
    global _redis_client

    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None
        logger.info("Redis client closed")


async def get_redis() -> AsyncGenerator[RedisCache, None]:
    """
    Dependency function to get Redis cache instance.

    Yields:
        RedisCache instance
    """
    client = await get_redis_client()
    cache = RedisCache(client)

    try:
        yield cache
    except Exception as e:
        logger.error(f"Error in Redis cache dependency: {e}")
        raise


# Cache key builders
def build_user_profile_key(user_id: str) -> str:
    """Build cache key for user profile."""
    return f"user:profile:{user_id}"


def build_journal_list_key(user_id: str, page: int, page_size: int) -> str:
    """Build cache key for journal entry list."""
    return f"journal:list:{user_id}:page:{page}:size:{page_size}"


def build_ai_response_key(user_id: str, message_hash: str) -> str:
    """Build cache key for AI agent response."""
    return f"ai:response:{user_id}:{message_hash}"


def build_conversation_key(user_id: str) -> str:
    """Build cache key for conversation history."""
    return f"conversation:{user_id}"


# Cache TTL constants (in seconds)
TTL_USER_PROFILE = 3600  # 1 hour
TTL_JOURNAL_LIST = 300  # 5 minutes
TTL_AI_RESPONSE = 86400  # 24 hours
TTL_CONVERSATION = 1800  # 30 minutes
