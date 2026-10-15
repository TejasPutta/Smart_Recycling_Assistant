"""Recycling guidance endpoint — Gemini with local fallback."""

from fastapi import APIRouter

from app.schemas.guidance import GuidanceRequest, GuidanceResponse
from app.services.guidance import gemini_service

router = APIRouter(tags=["Guidance"])


@router.post(
    "/guidance",
    response_model=GuidanceResponse,
    summary="Get recycling guidance for a scanned item",
    description=(
        "Returns step-by-step recycling guidance. Uses Google Gemini when "
        "configured. Falls back to local guidance on any failure — the "
        "response `source` field always tells you which was used."
    ),
)
async def get_guidance(payload: GuidanceRequest) -> GuidanceResponse:
    return gemini_service.get_guidance(
        label=payload.label,
        category=payload.category,
        confidence=payload.confidence,
    )