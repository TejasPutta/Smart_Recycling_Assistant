"""Unit tests for the reward service (in-memory SQLite)."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.database.base import Base
from app.models.reward import RewardTransaction  # noqa: F401 - register model
from app.schemas.rewards import AwardRewardRequest
from app.services.rewards import reward_service


@pytest.fixture()
def db() -> Session:
    """Fresh in-memory SQLite session per test."""
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        engine.dispose()


def test_balance_starts_at_zero(db: Session) -> None:
    balance = reward_service.get_balance(db, "user-1")
    assert balance.droplets == 0
    assert balance.tree_level == 0
    assert balance.tree_progress_pct == 0.0


def test_award_creates_transaction_and_updates_balance(db: Session) -> None:
    result = reward_service.award_for_disposal(
        db, AwardRewardRequest(user_id="user-1", scan_id=1)
    )
    assert result.awarded is True
    assert result.amount > 0
    assert result.balance.droplets == result.amount


def test_award_is_idempotent_per_scan(db: Session) -> None:
    first = reward_service.award_for_disposal(
        db, AwardRewardRequest(user_id="user-1", scan_id=42)
    )
    second = reward_service.award_for_disposal(
        db, AwardRewardRequest(user_id="user-1", scan_id=42)
    )
    assert first.awarded is True
    assert second.awarded is False
    assert second.amount == 0
    assert second.balance.droplets == first.balance.droplets


def test_different_scans_award_separately(db: Session) -> None:
    reward_service.award_for_disposal(
        db, AwardRewardRequest(user_id="user-1", scan_id=1)
    )
    reward_service.award_for_disposal(
        db, AwardRewardRequest(user_id="user-1", scan_id=2)
    )
    balance = reward_service.get_balance(db, "user-1")
    assert balance.droplets == 10  # 2 scans x 5 droplets


def test_history_lists_transactions(db: Session) -> None:
    reward_service.award_for_disposal(
        db, AwardRewardRequest(user_id="user-1", scan_id=1)
    )
    reward_service.award_for_disposal(
        db, AwardRewardRequest(user_id="user-1", scan_id=2)
    )
    history = reward_service.list_history(db, "user-1")
    assert history.total == 2
    assert len(history.items) == 2


def test_tree_level_increments_with_droplets(db: Session) -> None:
    for i in range(1, 11):
        reward_service.award_for_disposal(
            db, AwardRewardRequest(user_id="tree-user", scan_id=i)
        )
    balance = reward_service.get_balance(db, "tree-user")
    assert balance.droplets == 50
    assert balance.tree_level == 1
    assert balance.tree_progress_pct == 0.0