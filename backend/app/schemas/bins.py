"""Pydantic schemas for the digital-twin bin view.

Bins are VIRTUAL — they represent the accumulated volume of waste a user has
scanned, grouped by category. Nothing here reads real sensors.
"""

from __future__ import annotations

from pydantic import BaseModel, Field


class BinStatus(BaseModel):
    """Single virtual bin's state."""

    category: str
    fill_percentage: float = Field(..., ge=0.0, le=100.0)
    estimated_items: int = Field(..., ge=0)
    status: str = Field(..., description="empty | normal | filling | full")


class BinsResponse(BaseModel):
    """All virtual bins with a data-source note."""

    bins: list[BinStatus]
    total_items: int
    note: str = Field(
        default=(
            "Bins are virtual — values are derived from confirmed scans, "
            "not from physical sensors."
        )
    )