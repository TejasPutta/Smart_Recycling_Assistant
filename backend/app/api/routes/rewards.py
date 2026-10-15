"""Rewards endpoints: balance, award, history."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.schemas.rewards import (
    AwardRewardRequest,
    AwardRewardResponse,
    RewardBalance,
    RewardHistoryResponse,
)
from app.services.rewards import reward_service

router = APIRouter(tags=["Rewards"], prefix="/rewards")


@router.get(
    "/balance",
    response_model=RewardBalance,
    summary="Current droplet balance and tree level",
)
async def get_balance(
    user_id: str = Query(..., min_length=1, max_length=64),
    db: Session = Depends(get_db),
) -> RewardBalance:
    return reward_service.get_balance(db, user_id)


@router.post(
    "/award",
    response_model=AwardRewardResponse,
    summary="Award droplets for a confirmed disposal",
    description=(
        "Call this ONLY after the user explicitly confirms disposal. "
        "Idempotent: repeated calls with the same (user_id, scan_id) "
        "return awarded=false and do not create a second entry."
    ),
)
async def award(
    payload: AwardRewardRequest,
    db: Session = Depends(get_db),
) -> AwardRewardResponse:
    return reward_service.award_for_disposal(db, payload)


@router.get(
    "/history",
    response_model=RewardHistoryResponse,
    summary="Reward transaction history",
)
async def history(
    user_id: str = Query(..., min_length=1, max_length=64),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> RewardHistoryResponse:
    return reward_service.list_history(db, user_id, limit=limit, offset=offset)