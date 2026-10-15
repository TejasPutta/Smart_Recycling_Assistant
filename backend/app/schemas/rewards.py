"""Pydantic schemas for rewards endpoints."""

from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RewardBalance(BaseModel):
    """Current droplet balance and derived tree info for a user."""

    user_id: str
    droplets: int = Field(..., ge=0)
    tree_level: int = Field(..., ge=0, description="Derived from droplet count")
    tree_progress_pct: float = Field(
        ..., ge=0.0, le=100.0, description="Progress toward next tree level"
    )


class RewardTransactionItem(BaseModel):
    """One ledger entry."""

    id: int
    amount: int
    reason: str
    scan_id: Optional[int] = None
    created_at: datetime


class RewardHistoryResponse(BaseModel):
    """Paginated reward transaction history."""

    user_id: str
    total: int
    limit: int
    offset: int
    items: list[RewardTransactionItem]


class AwardRewardRequest(BaseModel):
    """Body for POST /api/v1/rewards/award."""

    user_id: str = Field(..., min_length=1, max_length=64)
    scan_id: int = Field(..., ge=1)
    reason: str = Field(default="confirmed disposal", max_length=255)


class AwardRewardResponse(BaseModel):
    """Response after attempting to award."""

    awarded: bool
    amount: int
    balance: RewardBalance
    note: Optional[str] = None