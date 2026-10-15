"""Dashboard statistics endpoints."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.statistics import StatisticsResponse
from app.services import statistics_service

router = APIRouter(tags=["Statistics"])


@router.get(
    "/statistics",
    response_model=StatisticsResponse,
    summary="Dashboard statistics",
    description=(
        "Total scans, category breakdown, recent activity, and time range — "
        "all computed from real records in the scans table."
    ),
)
async def get_statistics(db: Session = Depends(get_db)) -> StatisticsResponse:
    return statistics_service.get_statistics(db)