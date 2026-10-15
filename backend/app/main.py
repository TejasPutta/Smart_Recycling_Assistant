"""
FastAPI application entrypoint for Smart Recycling Assistant.

Run in development:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import bins as bins_routes
from app.api.routes import classification as classification_routes
from app.api.routes import guidance as guidance_routes
from app.api.routes import health as health_routes
from app.api.routes import history as history_routes
from app.api.routes import rewards as rewards_routes
from app.api.routes import statistics as statistics_routes
from app.core.config import get_settings
from app.database.connection import init_db

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Routers ----------
app.include_router(health_routes.router, prefix=settings.api_v1_prefix)
app.include_router(classification_routes.router, prefix=settings.api_v1_prefix)
app.include_router(history_routes.router, prefix=settings.api_v1_prefix)
app.include_router(guidance_routes.router, prefix=settings.api_v1_prefix)
app.include_router(statistics_routes.router, prefix=settings.api_v1_prefix)
app.include_router(bins_routes.router, prefix=settings.api_v1_prefix)
app.include_router(rewards_routes.router, prefix=settings.api_v1_prefix)


# ---------- Startup ----------
@app.on_event("startup")
def _startup_init_db() -> None:
    """Ensure database tables exist before serving requests."""
    init_db()


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