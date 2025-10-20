"""FastAPI main application."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api import auth_router, chat_router, health_router, journal_router
from .core.config import settings
from .core.database import init_db

# Create FastAPI application
app = FastAPI(
    title="Kai Backend",
    description="Mental wellness platform with multi-agent AI system",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(journal_router)


@app.on_event("startup")
async def startup_event() -> None:
    """Initialize database on startup."""
    await init_db()


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
