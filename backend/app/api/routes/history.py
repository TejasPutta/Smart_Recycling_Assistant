"""Scan history endpoints: save, list, and fetch individual records."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.scan import (
    SaveScanRequest,
    SaveScanResponse,
    ScanDetail,
    ScanHistoryPage,
)
from app.services import history_service

router = APIRouter(tags=["History"], prefix="/history")


@router.post(
    "",
    response_model=SaveScanResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Save a confirmed scan",
    description=(
        "Persist a classification result after the user confirms it. "
        "The frontend must only call this when the user actually confirms."
    ),
)
async def save_scan(
    payload: SaveScanRequest,
    db: Session = Depends(get_db),
) -> SaveScanResponse:
    scan = history_service.save_scan(db, payload)
    return SaveScanResponse(id=scan.id, created_at=scan.created_at)


@router.get(
    "",
    response_model=ScanHistoryPage,
    summary="List scan history",
    description="Paginated scan history, newest first, optionally filtered by category.",
)
async def list_scans(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    category: str | None = Query(None, description="Filter by waste category"),
    db: Session = Depends(get_db),
) -> ScanHistoryPage:
    return history_service.list_scans(db, limit=limit, offset=offset, category=category)


@router.get(
    "/{scan_id}",
    response_model=ScanDetail,
    summary="Get a single scan",
)
async def get_scan(
    scan_id: int,
    db: Session = Depends(get_db),
) -> ScanDetail:
    detail = history_service.get_scan(db, scan_id)
    if detail is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scan {scan_id} not found.",
        )
    return detail