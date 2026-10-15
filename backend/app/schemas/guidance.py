"""Pydantic schemas for recycling guidance endpoints."""

from __future__ import annotations

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class GuidanceSource(str, Enum):
    """Where the guidance came from."""

    GEMINI = "gemini"
    FALLBACK = "fallback"


class GuidanceRequest(BaseModel):
    """Body for POST /api/v1/guidance."""

    label: str = Field(..., min_length=1, max_length=255)
    category: str = Field(..., min_length=1, max_length=50)
    confidence: Optional[float] = Field(default=None, ge=0.0, le=1.0)


class GuidanceResponse(BaseModel):
    """Response body for POST /api/v1/guidance."""

    source: GuidanceSource
    label: str
    category: str
    recyclability: str = Field(
        ..., description="recyclable / conditional / not_recyclable / unknown"
    )
    guidance: str = Field(
        ..., description="Markdown-formatted step-by-step guidance"
    )
    note: Optional[str] = Field(
        default=None, description="Fallback reason if applicable"
    )