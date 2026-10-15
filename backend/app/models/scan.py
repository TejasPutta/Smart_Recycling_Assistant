"""
ORM model for stored scan records.

Each time a user classifies an image and confirms the result, we persist:
- the top predicted label + category + confidence
- all predictions as JSON (for detail view)
- creation timestamp
"""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Scan(Base):
    """A stored waste-scan record."""

    __tablename__ = "scans"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # Top prediction (denormalized for fast dashboard queries)
    label: Mapped[str] = mapped_column(String(255), nullable=False)
    category: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)

    # Full prediction list as JSON text (ordered, includes category_info)
    predictions_json: Mapped[str] = mapped_column(Text, nullable=False)

    # Where the prediction came from: "model" or "demo"
    source: Mapped[str] = mapped_column(String(20), nullable=False, default="model")

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=_utcnow,
        index=True,
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<Scan id={self.id} label={self.label!r} category={self.category}>"