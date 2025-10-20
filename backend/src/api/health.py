"""Health check endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter(prefix="/health", tags=["health"])


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


@router.get("", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint."""
    return HealthResponse(status="healthy", version="0.1.0")
