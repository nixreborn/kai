"""Performance monitoring middleware."""

import logging
import time
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger(__name__)


class PerformanceMiddleware(BaseHTTPMiddleware):
    """Middleware to track request performance."""

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process request and track performance.

        Args:
            request: HTTP request
            call_next: Next middleware/handler

        Returns:
            HTTP response with performance headers
        """
        start_time = time.perf_counter()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration = time.perf_counter() - start_time

        # Add performance header
        response.headers["X-Response-Time"] = f"{duration:.4f}s"

        # Log slow requests
        if duration > 1.0:
            logger.warning(
                f"Slow request: {request.method} {request.url.path} took {duration:.4f}s"
            )

        return response
