"""Persist and query scan records in SQLite."""

from __future__ import annotations

import json
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.scan import Scan
from app.schemas.classification import ClassificationSource
from app.schemas.scan import (
    SaveScanRequest,
    ScanDetail,
    ScanHistoryPage,
    ScanSummary,
)


def save_scan(db: Session, payload: SaveScanRequest) -> Scan:
    """Insert a new scan record. Returns the persisted row (with id)."""
    scan = Scan(
        label=payload.label,
        category=payload.category,
        confidence=payload.confidence,
        source=payload.source.value,
        predictions_json=json.dumps(
            [p.model_dump(mode="json") for p in payload.predictions]
        ),
    )
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


def _to_summary(scan: Scan) -> ScanSummary:
    return ScanSummary(
        id=scan.id,
        label=scan.label,
        category=scan.category,
        confidence=scan.confidence,
        source=ClassificationSource(scan.source),
        created_at=scan.created_at,
    )


def list_scans(
    db: Session,
    limit: int = 20,
    offset: int = 0,
    category: Optional[str] = None,
) -> ScanHistoryPage:
    """Return a paginated, optionally category-filtered history."""
    stmt = select(Scan)
    count_stmt = select(func.count()).select_from(Scan)

    if category:
        stmt = stmt.where(Scan.category == category)
        count_stmt = count_stmt.where(Scan.category == category)

    total = db.execute(count_stmt).scalar_one()
    stmt = stmt.order_by(Scan.created_at.desc()).limit(limit).offset(offset)
    rows = db.execute(stmt).scalars().all()

    return ScanHistoryPage(
        total=total,
        limit=limit,
        offset=offset,
        items=[_to_summary(r) for r in rows],
    )


def get_scan(db: Session, scan_id: int) -> Optional[ScanDetail]:
    """Return the full detail of one scan, or None if not found."""
    row = db.get(Scan, scan_id)
    if row is None:
        return None

    try:
        raw = json.loads(row.predictions_json) if row.predictions_json else []
    except json.JSONDecodeError:
        raw = []

    return ScanDetail(
        id=row.id,
        label=row.label,
        category=row.category,
        confidence=row.confidence,
        source=ClassificationSource(row.source),
        created_at=row.created_at,
        predictions=raw,
    )