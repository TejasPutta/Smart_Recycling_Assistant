"""Pydantic schemas for dashboard statistics."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class CategoryCount(BaseModel):
    category: str
    count: int
    percentage: float = Field(..., ge=0.0, le=100.0)


class RecentScanItem(BaseModel):
    id: int
    label: str
    category: str
    confidence: float
    created_at: datetime


class StatisticsResponse(BaseModel):
    """Dashboard statistics computed from real scan records."""

    total_scans: int
    categories: list[CategoryCount]
    recent: list[RecentScanItem]
    first_scan_at: Optional[datetime] = None
    last_scan_at: Optional[datetime] = None