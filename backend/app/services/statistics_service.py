"""Compute dashboard statistics from real scan records."""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.scan import Scan
from app.schemas.bins import BinsResponse, BinStatus
from app.schemas.statistics import (
    CategoryCount,
    RecentScanItem,
    StatisticsResponse,
)


def _status_for(fill_pct: float, count: int) -> str:
    if count == 0:
        return "empty"
    if fill_pct >= 90:
        return "full"
    if fill_pct >= 60:
        return "filling"
    return "normal"


def get_statistics(db: Session, recent_limit: int = 10) -> StatisticsResponse:
    """Return dashboard stats derived entirely from the scans table."""
    total = db.execute(select(func.count()).select_from(Scan)).scalar_one()

    # Category breakdown
    rows = db.execute(
        select(Scan.category, func.count(Scan.id))
        .group_by(Scan.category)
        .order_by(func.count(Scan.id).desc())
    ).all()

    categories: list[CategoryCount] = []
    for category, count in rows:
        pct = (count / total * 100.0) if total else 0.0
        categories.append(
            CategoryCount(
                category=category,
                count=count,
                percentage=round(pct, 2),
            )
        )

    # Recent scans
    recent_rows = (
        db.execute(
            select(Scan).order_by(Scan.created_at.desc()).limit(recent_limit)
        )
        .scalars()
        .all()
    )
    recent = [
        RecentScanItem(
            id=r.id,
            label=r.label,
            category=r.category,
            confidence=r.confidence,
            created_at=r.created_at,
        )
        for r in recent_rows
    ]

    # Time range
    first_at = db.execute(select(func.min(Scan.created_at))).scalar_one()
    last_at = db.execute(select(func.max(Scan.created_at))).scalar_one()

    return StatisticsResponse(
        total_scans=total,
        categories=categories,
        recent=recent,
        first_scan_at=first_at,
        last_scan_at=last_at,
    )


# Virtual bins: how many scans we need per category before the bin is "full".
# These are DEMO assumptions, clearly documented.
_BIN_CAPACITY_PER_CATEGORY = 25


def get_bins(db: Session) -> BinsResponse:
    """Build the digital-twin bin view from scan counts."""
    rows = db.execute(
        select(Scan.category, func.count(Scan.id)).group_by(Scan.category)
    ).all()

    by_category = {category: count for category, count in rows}

    # Show a bin for every known category, even empty ones, for the UI
    from app.schemas.classification import WasteCategory

    bins: list[BinStatus] = []
    total_items = 0
    for cat in WasteCategory:
        count = by_category.get(cat.value, 0)
        total_items += count
        fill_pct = min(100.0, count / _BIN_CAPACITY_PER_CATEGORY * 100.0)
        bins.append(
            BinStatus(
                category=cat.value,
                fill_percentage=round(fill_pct, 2),
                estimated_items=count,
                status=_status_for(fill_pct, count),
            )
        )

    return BinsResponse(bins=bins, total_items=total_items)