"""
Gemini-powered recycling guidance with a local fallback.

Design:
- Gemini is OPTIONAL. No key -> fallback immediately.
- Every Gemini call is wrapped: any failure falls back to local guidance.
- The fallback is clearly labeled in the response source, never faked.
"""

from __future__ import annotations

import logging
from typing import Optional

from app.core.config import get_settings
from app.schemas.guidance import GuidanceResponse, GuidanceSource
from app.services.classification.category_mapper import map_label_to_category

logger = logging.getLogger(__name__)

_PROMPT_TEMPLATE = (
    "You are a recycling expert. A user has scanned a waste item.\n"
    "Item label: {label}\n"
    "Waste category: {category}\n"
    "Give concise, practical, step-by-step recycling guidance in Markdown.\n"
    "Include: (1) recyclability verdict, (2) preparation steps, "
    "(3) where to dispose of it, (4) one reuse tip if relevant, "
    "(5) a note that local rules vary.\n"
    "Keep it under 200 words. Be specific, no fluff."
)


def _local_fallback(label: str, category: str, reason: str) -> GuidanceResponse:
    """Generate honest local guidance using our own category mapper."""
    info = map_label_to_category(label or "")
    effective_category = category or info.category.value

    guidance_md = (
        f"### {info.display_name}\n\n"
        f"**Recyclability:** {info.recyclability.value.replace('_', ' ')}\n\n"
        f"**Advice:** {info.short_advice}\n\n"
        f"_Local rules vary. Check your municipality's website for the "
        f"latest guidance on **{effective_category}** waste._"
    )

    return GuidanceResponse(
        source=GuidanceSource.FALLBACK,
        label=label,
        category=effective_category,
        recyclability=info.recyclability.value,
        guidance=guidance_md,
        note=reason,
    )


def get_guidance(
    label: str,
    category: str,
    confidence: Optional[float] = None,
) -> GuidanceResponse:
    """Return recycling guidance. Gemini if configured, else local fallback."""
    settings = get_settings()

    if not settings.gemini_api_key:
        return _local_fallback(
            label,
            category,
            "Gemini API key not configured; using local guidance.",
        )

    try:
        from google import genai  # type: ignore
        from google.genai import types as genai_types  # type: ignore

        client = genai.Client(api_key=settings.gemini_api_key)
        prompt = _PROMPT_TEMPLATE.format(label=label, category=category)

        response = client.models.generate_content(
            model=settings.gemini_model,
            contents=prompt,
            config=genai_types.GenerateContentConfig(
                temperature=0.4,
                max_output_tokens=400,
            ),
        )

        text = (response.text or "").strip()
        if not text:
            return _local_fallback(
                label,
                category,
                "Gemini returned empty response; using local guidance.",
            )

        info = map_label_to_category(label or "")

        return GuidanceResponse(
            source=GuidanceSource.GEMINI,
            label=label,
            category=category or info.category.value,
            recyclability=info.recyclability.value,
            guidance=text,
            note=None,
        )

    except Exception as exc:
        logger.warning(
            "Gemini guidance failed: %s: %s", type(exc).__name__, exc
        )
        return _local_fallback(
            label,
            category,
            f"Gemini call failed ({type(exc).__name__}); using local guidance.",
        )