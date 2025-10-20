"""Performance metrics collection and monitoring."""

import logging
import time
from collections import defaultdict
from collections.abc import Callable
from functools import wraps
from typing import Any

logger = logging.getLogger(__name__)

# In-memory metrics storage (use Redis or proper metrics backend in production)
_endpoint_metrics: dict[str, dict[str, Any]] = defaultdict(
    lambda: {
        "count": 0,
        "total_time": 0.0,
        "min_time": float("inf"),
        "max_time": 0.0,
        "errors": 0,
    }
)

_slow_queries: list[dict[str, Any]] = []
SLOW_QUERY_THRESHOLD = 0.1  # 100ms


def performance_timer(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator to time function execution.

    Args:
        func: Function to time

    Returns:
        Wrapped function with timing
    """

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            result = await func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start_time
            logger.debug(f"{func.__name__} took {elapsed:.4f}s")

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        start_time = time.perf_counter()
        try:
            result = func(*args, **kwargs)
            return result
        finally:
            elapsed = time.perf_counter() - start_time
            logger.debug(f"{func.__name__} took {elapsed:.4f}s")

    # Return appropriate wrapper based on whether function is async
    import inspect

    if inspect.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper


def track_endpoint_performance(endpoint: str) -> Callable[..., Any]:
    """
    Decorator to track endpoint performance metrics.

    Args:
        endpoint: Endpoint identifier (e.g., "POST /api/chat")

    Returns:
        Decorator function
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @wraps(func)
        async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            error = False

            try:
                result = await func(*args, **kwargs)
                return result
            except Exception:
                error = True
                raise
            finally:
                elapsed = time.perf_counter() - start_time

                # Update metrics
                metrics = _endpoint_metrics[endpoint]
                metrics["count"] += 1
                metrics["total_time"] += elapsed
                metrics["min_time"] = min(metrics["min_time"], elapsed)
                metrics["max_time"] = max(metrics["max_time"], elapsed)
                if error:
                    metrics["errors"] += 1

                # Log slow requests
                if elapsed > 1.0:  # Log requests over 1 second
                    logger.warning(f"Slow endpoint: {endpoint} took {elapsed:.4f}s")

        @wraps(func)
        def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.perf_counter()
            error = False

            try:
                result = func(*args, **kwargs)
                return result
            except Exception:
                error = True
                raise
            finally:
                elapsed = time.perf_counter() - start_time

                # Update metrics
                metrics = _endpoint_metrics[endpoint]
                metrics["count"] += 1
                metrics["total_time"] += elapsed
                metrics["min_time"] = min(metrics["min_time"], elapsed)
                metrics["max_time"] = max(metrics["max_time"], elapsed)
                if error:
                    metrics["errors"] += 1

                # Log slow requests
                if elapsed > 1.0:
                    logger.warning(f"Slow endpoint: {endpoint} took {elapsed:.4f}s")

        import inspect

        if inspect.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper

    return decorator


def log_slow_query(query: str, duration: float, params: dict[str, Any] | None = None) -> None:
    """
    Log slow database queries.

    Args:
        query: SQL query
        duration: Query duration in seconds
        params: Query parameters (optional)
    """
    if duration > SLOW_QUERY_THRESHOLD:
        slow_query = {
            "query": query,
            "duration": duration,
            "params": params,
            "timestamp": time.time(),
        }
        _slow_queries.append(slow_query)

        # Keep only last 100 slow queries
        if len(_slow_queries) > 100:
            _slow_queries.pop(0)

        logger.warning(
            f"Slow query ({duration:.4f}s): {query[:100]}..."
            + (f" params={params}" if params else "")
        )


def get_performance_metrics() -> dict[str, Any]:
    """
    Get current performance metrics.

    Returns:
        Dictionary of performance metrics
    """
    # Calculate averages and format metrics
    formatted_metrics = {}

    for endpoint, metrics in _endpoint_metrics.items():
        count = metrics["count"]
        if count > 0:
            formatted_metrics[endpoint] = {
                "count": count,
                "avg_time": metrics["total_time"] / count,
                "min_time": metrics["min_time"],
                "max_time": metrics["max_time"],
                "error_rate": metrics["errors"] / count if count > 0 else 0,
            }

    return {
        "endpoints": formatted_metrics,
        "slow_queries": _slow_queries[-10:],  # Last 10 slow queries
        "slow_query_count": len(_slow_queries),
    }


def reset_metrics() -> None:
    """Reset all performance metrics."""
    global _endpoint_metrics, _slow_queries
    _endpoint_metrics.clear()
    _slow_queries.clear()
    logger.info("Performance metrics reset")
