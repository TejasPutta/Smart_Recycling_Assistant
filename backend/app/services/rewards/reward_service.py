"""
Reward service: award droplets for confirmed disposals, compute balance,
track tree growth. Idempotent — one reward per scan per user.
"""

from __future__ import annotations

import json
import logging

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.reward import RewardTransaction
from app.schemas.rewards import (
    AwardRewardRequest,
    AwardRewardResponse,
    RewardBalance,
    RewardHistoryResponse,
    RewardTransactionItem,
)

logger = logging.getLogger(__name__)

# Game design constants — documented for the hackathon demo
_DROPLETS_PER_DISPOSAL = 5
_DROPLETS_PER_TREE_LEVEL = 50


def _compute_balance(db: Session, user_id: str) -> RewardBalance:
    """Sum all transactions for the user and derive tree level."""
    total = (
        db.execute(
            select(func.coalesce(func.sum(RewardTransaction.amount), 0)).where(
                RewardTransaction.user_id == user_id
            )
        ).scalar_one()
        or 0
    )
    total = max(int(total), 0)  # never report negative

    tree_level = total // _DROPLETS_PER_TREE_LEVEL
    remainder = total % _DROPLETS_PER_TREE_LEVEL
    progress = (remainder / _DROPLETS_PER_TREE_LEVEL) * 100.0

    return RewardBalance(
        user_id=user_id,
        droplets=total,
        tree_level=int(tree_level),
        tree_progress_pct=round(progress, 2),
    )


def get_balance(db: Session, user_id: str) -> RewardBalance:
    """Public: return the current balance for a user."""
    return _compute_balance(db, user_id)


def award_for_disposal(
    db: Session, payload: AwardRewardRequest
) -> AwardRewardResponse:
    """
    Award droplets for a confirmed disposal.

    Idempotent: if a reward already exists for (user_id, scan_id),
    we return awarded=False and do NOT create a second entry.
    """
    existing = db.execute(
        select(RewardTransaction).where(
            RewardTransaction.user_id == payload.user_id,
            RewardTransaction.scan_id == payload.scan_id,
        )
    ).scalar_one_or_none()

    if existing is not None:
        return AwardRewardResponse(
            awarded=False,
            amount=0,
            balance=_compute_balance(db, payload.user_id),
            note="Reward already granted for this scan.",
        )

    tx = RewardTransaction(
        user_id=payload.user_id,
        scan_id=payload.scan_id,
        amount=_DROPLETS_PER_DISPOSAL,
        reason=payload.reason,
        metadata_json=json.dumps({"source": "award_for_disposal"}),
    )
    db.add(tx)
    try:
        db.commit()
    except IntegrityError:
        # Race condition — another request inserted first. Treat as duplicate.
        db.rollback()
        return AwardRewardResponse(
            awarded=False,
            amount=0,
            balance=_compute_balance(db, payload.user_id),
            note="Reward already granted (concurrent request).",
        )

    return AwardRewardResponse(
        awarded=True,
        amount=_DROPLETS_PER_DISPOSAL,
        balance=_compute_balance(db, payload.user_id),
        note=None,
    )


def list_history(
    db: Session, user_id: str, limit: int = 20, offset: int = 0
) -> RewardHistoryResponse:
    """Return paginated reward transaction history for a user."""
    count_stmt = (
        select(func.count())
        .select_from(RewardTransaction)
        .where(RewardTransaction.user_id == user_id)
    )
    total = db.execute(count_stmt).scalar_one()

    rows = (
        db.execute(
            select(RewardTransaction)
            .where(RewardTransaction.user_id == user_id)
            .order_by(RewardTransaction.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        .scalars()
        .all()
    )

    return RewardHistoryResponse(
        user_id=user_id,
        total=total,
        limit=limit,
        offset=offset,
        items=[
            RewardTransactionItem(
                id=r.id,
                amount=r.amount,
                reason=r.reason,
                scan_id=r.scan_id,
                created_at=r.created_at,
            )
            for r in rows
        ],
    )