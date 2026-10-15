"""Health-check route for the Smart Recycling Assistant API."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field

from app.core.config import Settings, get_settings

router = APIRouter(tags=["Health"])


class HealthResponse(BaseModel):
    """Response schema for GET /health."""

    status: str = Field(..., examples=["ok"])
    service: str = Field(..., examples=["Smart Recycling Assistant API"])
    version: str = Field(..., examples=["0.1.0"])
    environment: str = Field(..., examples=["development"])
    timestamp: str = Field(..., description="UTC ISO-8601 timestamp")


@router.get(
    "/health",
    response_model=HealthResponse,
    summary="Service health check",
    description="Returns basic service status. Safe to poll from monitoring tools.",
)
async def health_check(settings: Settings = Depends(get_settings)) -> HealthResponse:
    """Return the current service health status."""
    return HealthResponse(
        status="ok",
        service=settings.app_name,
        version=settings.app_version,
        environment=settings.app_env,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )