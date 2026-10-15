"""
ORM model for reward transactions (water droplets).

Each confirmed disposal awards droplets. Balance is computed by summing
this ledger — never stored directly (avoids race conditions).
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class RewardTransaction(Base):
    """One ledger entry — droplets awarded (or spent) for a user."""

    __tablename__ = "reward_transactions"
    __table_args__ = (
        # Prevent duplicate rewards for the same scan
        UniqueConstraint("user_id", "scan_id", name="uq_user_scan_reward"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)

    # Linked scan (nullable for bonus/spend operations)
    scan_id: Mapped[int | None] = mapped_column(Integer, nullable=True, index=True)

    # Positive = awarded, negative = spent
    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    reason: Mapped[str] = mapped_column(String(255), nullable=False)
    metadata_json: Mapped[str | None] = mapped_column(Text, nullable=True)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        index=True,
    )

    def __repr__(self) -> str:  # pragma: no cover
        return (
            f"<RewardTransaction id={self.id} user={self.user_id} "
            f"amount={self.amount}>"
        )