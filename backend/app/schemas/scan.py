"""Pydantic schemas for scan history endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.classification import ClassificationPrediction, ClassificationSource


class ScanSummary(BaseModel):
    """Condensed scan record for list views."""

    id: int
    label: str
    category: str
    confidence: float
    source: ClassificationSource
    created_at: datetime


class ScanDetail(BaseModel):
    """Full scan record with all predictions."""

    id: int
    label: str
    category: str
    confidence: float
    source: ClassificationSource
    created_at: datetime
    predictions: list[ClassificationPrediction] = Field(default_factory=list)


class ScanHistoryPage(BaseModel):
    """Paginated scan history response."""

    total: int = Field(..., description="Total matching records")
    limit: int
    offset: int
    items: list[ScanSummary]


class SaveScanRequest(BaseModel):
    """Body for POST /api/v1/history — persist a confirmed classification."""

    label: str
    category: str
    confidence: float
    source: ClassificationSource = ClassificationSource.MODEL
    predictions: list[ClassificationPrediction] = Field(default_factory=list)


class SaveScanResponse(BaseModel):
    """Response after saving a scan."""

    id: int
    created_at: datetime