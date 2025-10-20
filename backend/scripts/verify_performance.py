#!/usr/bin/env python3
"""Verification script for performance optimizations."""

import asyncio
import sys
import time
from pathlib import Path

# Add backend src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


async def check_redis_connection() -> bool:
    """Check Redis connection."""
    try:
        from cache.redis_client import get_redis_client, RedisCache

        print("Checking Redis connection...")
        client = await get_redis_client()
        cache = RedisCache(client)

        # Test ping
        is_available = await cache.ping()
        if not is_available:
            print("  FAIL: Redis ping failed")
            return False

        # Test set/get
        test_key = "test:performance:verification"
        await cache.set(test_key, "test_value", ttl=10)
        value = await cache.get(test_key)
        await cache.delete(test_key)

        if value != "test_value":
            print("  FAIL: Redis set/get test failed")
            return False

        print("  PASS: Redis is connected and working")
        return True

    except ImportError as e:
        print(f"  FAIL: Import error - {e}")
        return False
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def check_database_indexes() -> bool:
    """Check if performance indexes exist."""
    try:
        from sqlalchemy import inspect, text
        from core.database import engine

        print("Checking database indexes...")

        async with engine.connect() as conn:
            # Check for created_at index on journal_entries
            result = await conn.execute(
                text(
                    """
                SELECT indexname FROM pg_indexes
                WHERE tablename = 'journal_entries'
                AND indexname LIKE '%created_at%';
            """
                )
            )
            indexes = [row[0] for row in result]

            if not indexes:
                print("  FAIL: No created_at indexes found on journal_entries")
                return False

            print(f"  PASS: Found indexes: {', '.join(indexes)}")
            return True

    except ImportError as e:
        print(f"  FAIL: Import error - {e}")
        return False
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def check_cache_key_builders() -> bool:
    """Check cache key builder functions."""
    try:
        from cache.redis_client import (
            build_ai_response_key,
            build_conversation_key,
            build_journal_list_key,
            build_user_profile_key,
        )

        print("Checking cache key builders...")

        # Test key builders
        user_key = build_user_profile_key("user123")
        assert user_key == "user:profile:user123", "User profile key incorrect"

        journal_key = build_journal_list_key("user123", 1, 20)
        assert (
            journal_key == "journal:list:user123:page:1:size:20"
        ), "Journal list key incorrect"

        conv_key = build_conversation_key("user123")
        assert conv_key == "conversation:user123", "Conversation key incorrect"

        ai_key = build_ai_response_key("user123", "abc123")
        assert ai_key == "ai:response:user123:abc123", "AI response key incorrect"

        print("  PASS: All cache key builders working")
        return True

    except ImportError as e:
        print(f"  FAIL: Import error - {e}")
        return False
    except AssertionError as e:
        print(f"  FAIL: {e}")
        return False
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def check_monitoring_metrics() -> bool:
    """Check monitoring metrics module."""
    try:
        from monitoring.metrics import (
            get_performance_metrics,
            log_slow_query,
            performance_timer,
            track_endpoint_performance,
        )

        print("Checking monitoring metrics...")

        # Test performance timer
        @performance_timer
        async def test_async_func():
            await asyncio.sleep(0.01)
            return "done"

        result = await test_async_func()
        assert result == "done", "Performance timer failed"

        # Test slow query logging
        log_slow_query("SELECT * FROM test", 0.15, {"id": 1})

        # Test metrics retrieval
        metrics = get_performance_metrics()
        assert isinstance(metrics, dict), "Metrics should return dict"
        assert "endpoints" in metrics, "Metrics should have endpoints"
        assert "slow_queries" in metrics, "Metrics should have slow_queries"

        print("  PASS: Monitoring metrics working")
        return True

    except ImportError as e:
        print(f"  FAIL: Import error - {e}")
        return False
    except AssertionError as e:
        print(f"  FAIL: {e}")
        return False
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def check_middleware() -> bool:
    """Check middleware modules."""
    try:
        from api.middleware import CompressionMiddleware, PerformanceMiddleware

        print("Checking middleware...")

        # Just check they can be imported and instantiated
        assert CompressionMiddleware is not None, "CompressionMiddleware not found"
        assert PerformanceMiddleware is not None, "PerformanceMiddleware not found"

        print("  PASS: Middleware modules available")
        return True

    except ImportError as e:
        print(f"  FAIL: Import error - {e}")
        return False
    except AssertionError as e:
        print(f"  FAIL: {e}")
        return False
    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def performance_benchmark() -> bool:
    """Run simple performance benchmark."""
    try:
        from cache.redis_client import get_redis_client, RedisCache

        print("Running performance benchmark...")

        client = await get_redis_client()
        cache = RedisCache(client)

        # Benchmark set operations
        start = time.perf_counter()
        for i in range(100):
            await cache.set(f"bench:key:{i}", f"value_{i}", ttl=10)
        set_time = time.perf_counter() - start

        # Benchmark get operations
        start = time.perf_counter()
        for i in range(100):
            await cache.get(f"bench:key:{i}")
        get_time = time.perf_counter() - start

        # Cleanup
        await cache.delete_pattern("bench:*")

        print(f"  100 SET operations: {set_time*1000:.2f}ms")
        print(f"  100 GET operations: {get_time*1000:.2f}ms")
        print(f"  Average SET: {set_time*10:.2f}ms")
        print(f"  Average GET: {get_time*10:.2f}ms")

        if get_time * 10 > 5:  # Average GET should be under 5ms
            print("  WARNING: Cache operations seem slow")
            return False

        print("  PASS: Performance benchmark completed")
        return True

    except Exception as e:
        print(f"  FAIL: {e}")
        return False


async def main():
    """Run all verification checks."""
    print("=" * 60)
    print("Performance Optimization Verification")
    print("=" * 60)
    print()

    results = {}

    # Run checks
    results["Redis Connection"] = await check_redis_connection()
    print()

    results["Database Indexes"] = await check_database_indexes()
    print()

    results["Cache Key Builders"] = await check_cache_key_builders()
    print()

    results["Monitoring Metrics"] = await check_monitoring_metrics()
    print()

    results["Middleware"] = await check_middleware()
    print()

    results["Performance Benchmark"] = await performance_benchmark()
    print()

    # Summary
    print("=" * 60)
    print("Summary")
    print("=" * 60)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for check, result in results.items():
        status = "PASS" if result else "FAIL"
        symbol = "✓" if result else "✗"
        print(f"{symbol} {check}: {status}")

    print()
    print(f"Total: {passed}/{total} checks passed")

    if passed == total:
        print("\nAll performance optimizations verified successfully!")
        return 0
    else:
        print("\nSome checks failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
