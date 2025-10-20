"""FastAPI main application."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from .api import auth_router, chat_router, documents_router, health_router, journal_router
from .api.middleware import CompressionMiddleware, PerformanceMiddleware
from .cache.redis_client import close_redis_client
from .core.config import settings
from .core.database import init_db
from .security.middleware import SecurityHeadersMiddleware
from .security.rate_limiter import limiter

# Create FastAPI application
app = FastAPI(
    title="Kai Backend",
    description="Mental wellness platform with multi-agent AI system",
    version="0.1.0",
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)

# Add rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Security Headers Middleware (add first for all responses)
app.add_middleware(SecurityHeadersMiddleware)

# Trusted Host Middleware (prevent host header attacks in production)
if not settings.debug:
    allowed_hosts = ["kai.example.com", "localhost", "127.0.0.1", "*.kai.example.com"]
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)

# Configure CORS with production-ready settings
cors_origins = settings.cors_origins_list if settings.debug else ["https://kai.example.com"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"],
)

# Add performance middleware
app.add_middleware(PerformanceMiddleware)

# Add compression middleware
app.add_middleware(CompressionMiddleware, minimum_size=500)

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(journal_router)
app.include_router(documents_router)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database on startup."""
    await init_db()


@app.on_event("shutdown")
async def shutdown_event() -> None:
    """Cleanup on shutdown."""
    await close_redis_client()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Kai Backend API",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
