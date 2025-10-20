"""Minimal FastAPI app for testing auth only."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import auth router directly to avoid importing agents
import sys
import importlib.util

spec = importlib.util.spec_from_file_location("auth", "src/api/auth.py")
auth_module = importlib.util.module_from_spec(spec)
sys.modules["auth"] = auth_module
spec.loader.exec_module(auth_module)

from src.core.config import settings
from src.core.database import init_db

# Create minimal FastAPI application
app = FastAPI(
    title="Kai Backend - Auth Test",
    description="Testing authentication endpoints only",
    version="0.1.0",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include only auth router
app.include_router(auth_module.router)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database on startup."""
    await init_db()


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "Kai Backend API - Auth Test",
        "version": "0.1.0",
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "test_app:app",
        host=settings.host,
        port=settings.port,
        reload=False,
    )
