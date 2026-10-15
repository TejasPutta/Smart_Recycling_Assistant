"""Virtual bin (digital-twin) endpoints.

IMPORTANT: these bins are VIRTUAL. They are derived from confirmed scans,
not from physical sensors or IoT hardware.
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.bins import BinsResponse
from app.services import statistics_service

router = APIRouter(tags=["Bins"])


@router.get(
    "/bins",
    response_model=BinsResponse,
    summary="Virtual bin fill levels",
    description=(
        "Returns fill levels for the digital-twin bins. Values are derived "
        "from confirmed scans — not from physical sensors."
    ),
)
async def get_bins(db: Session = Depends(get_db)) -> BinsResponse:
    return statistics_service.get_bins(db)