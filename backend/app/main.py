"""
FastAPI application entrypoint for Smart Recycling Assistant.

Run in development:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import health as health_routes
from app.core.config import get_settings

settings = get_settings()

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description=(
        "Backend API for the Smart Recycling Assistant hackathon project. "
        "Provides waste classification, scanning, guidance, disposal history, "
        "bin statistics, and recycling rewards."
    ),
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# ---------- CORS ----------
# Allow the separately-hosted frontend (Mayank's app) to call this API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Routers ----------
app.include_router(
    health_routes.router,
    prefix=settings.api_v1_prefix,
)


# ---------- Root endpoint ----------
@app.get("/", tags=["Root"], summary="API information")
async def root() -> JSONResponse:
    """Friendly landing endpoint describing the API."""
    return JSONResponse(
        {
            "service": settings.app_name,
            "version": settings.app_version,
            "environment": settings.app_env,
            "docs": "/docs",
            "redoc": "/redoc",
            "openapi": "/openapi.json",
            "health": f"{settings.api_v1_prefix}/health",
        }
    )