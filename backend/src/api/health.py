"""Health check endpoints."""

import time
from typing import Any

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ..cache.redis_client import RedisCache, get_redis
from ..core.database import get_db
from ..core.llm_client import check_llm_health
from ..monitoring.metrics import get_performance_metrics

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
    llm: dict[str, Any] | None = None


class DetailedHealthResponse(BaseModel):
    """Detailed health check response."""

    status: str
    version: str
    database: dict[str, Any]
    redis: dict[str, Any]
    llm: dict[str, Any]
    performance: dict[str, Any]


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns overall system health including LLM service status.
    """
    # Check LLM health
    llm_health = await check_llm_health()

    # Determine overall status
    overall_status = "healthy"
    if llm_health.get("status") == "unhealthy":
        overall_status = "degraded"

    return HealthResponse(
        status=overall_status,
        version="0.1.0",
        llm=llm_health,
    )


@router.get("/detailed", response_model=DetailedHealthResponse)
async def detailed_health_check(
    db: AsyncSession = Depends(get_db),
    cache: RedisCache = Depends(get_redis),
) -> DetailedHealthResponse:
    """
    Detailed health check endpoint with database, Redis, and LLM status.

    Checks:
    - Database connection and query time
    - Redis connection and ping time
    - LLM service status
    - Performance metrics
    """
    # Check database
    db_start = time.perf_counter()
    db_status = "healthy"
    db_error = None

    try:
        result = await db.execute(text("SELECT 1"))
        result.scalar()
    except Exception as e:
        db_status = "unhealthy"
        db_error = str(e)

    db_time = time.perf_counter() - db_start

    # Check Redis
    redis_start = time.perf_counter()
    redis_status = "healthy"
    redis_error = None

    try:
        redis_available = await cache.ping()
        if not redis_available:
            redis_status = "unhealthy"
            redis_error = "Redis ping failed"
    except Exception as e:
        redis_status = "unhealthy"
        redis_error = str(e)

    redis_time = time.perf_counter() - redis_start

    # Check LLM health
    llm_health = await check_llm_health()

    # Get performance metrics
    metrics = get_performance_metrics()

    # Overall status
    overall_status = "healthy"
    if db_status == "unhealthy" or redis_status == "unhealthy":
        overall_status = "degraded"
    if llm_health.get("status") == "unhealthy":
        overall_status = "degraded"

    return DetailedHealthResponse(
        status=overall_status,
        version="0.1.0",
        database={
            "status": db_status,
            "response_time_ms": round(db_time * 1000, 2),
            "error": db_error,
        },
        redis={
            "status": redis_status,
            "response_time_ms": round(redis_time * 1000, 2),
            "error": redis_error,
        },
        llm=llm_health,
        performance=metrics,
    )
