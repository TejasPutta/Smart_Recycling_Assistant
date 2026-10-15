"""
SQLite database engine, session factory, and initialization helpers.

The DB file path comes from settings.database_url (default: ./smart_recycling.db).
"""

from __future__ import annotations

import logging
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings
from app.database.base import Base

logger = logging.getLogger(__name__)

settings = get_settings()

# SQLite needs check_same_thread=False to work with FastAPI's threadpool
_engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False}
    if settings.database_url.startswith("sqlite")
    else {},
    echo=False,
    future=True,
)

SessionLocal = sessionmaker(
    bind=_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
    class_=Session,
)


def get_db() -> Iterator[Session]:
    """FastAPI dependency that yields a DB session and closes it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Create tables if they don't exist.

    Import all models BEFORE calling this so SQLAlchemy registers them
    on the Base metadata.
    """
    # Import side effect: registers models on Base.metadata
    from app.models import scan as _scan  # noqa: F401

    Base.metadata.create_all(bind=_engine)
    logger.info("Database initialized at %s", settings.database_url)


def get_engine():
    """Expose the engine for tests/utilities."""
    return _engine