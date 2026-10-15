"""
Pydantic schemas for the waste classification API.

These define the wire format for `/api/v1/classify`. Keep field names
stable — the frontend depends on them.
"""

from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WasteCategory(str, Enum):
    """Normalized waste categories used across the app."""

    PLASTIC = "plastic"
    PAPER = "paper"
    FABRIC = "fabric"
    BATTERY = "battery"
    CHEMICAL = "chemical"
    HAZARDOUS = "hazardous"
    BIODEGRADABLE = "biodegradable"
    OTHER = "other"


class Recyclability(str, Enum):
    """High-level recyclability verdict."""

    RECYCLABLE = "recyclable"
    CONDITIONAL = "conditional"
    NOT_RECYCLABLE = "not_recyclable"
    UNKNOWN = "unknown"


class ClassificationSource(str, Enum):
    """Where the prediction came from."""

    MODEL = "model"       # real inference from a loaded model
    DEMO = "demo"         # fallback when no model is available


class CategoryInfo(BaseModel):
    """Metadata about a waste category, returned alongside predictions."""

    category: WasteCategory
    display_name: str = Field(..., examples=["Plastic"])
    recyclability: Recyclability
    short_advice: str = Field(
        ...,
        examples=["Rinse and place in the plastics recycling bin."],
    )


class ClassificationPrediction(BaseModel):
    """One predicted label with its confidence and mapped category."""

    label: str = Field(..., examples=["water bottle"])
    category: WasteCategory
    confidence: float = Field(..., ge=0.0, le=1.0, examples=[0.87])
    category_info: CategoryInfo


class ClassificationResponse(BaseModel):
    """Response body for POST /api/v1/classify."""

    source: ClassificationSource
    model_name: Optional[str] = Field(
        default=None,
        description="Identifier of the model that produced the prediction (if source=model).",
        examples=["mobilenet_v3_large_imagenet"],
    )
    predictions: list[ClassificationPrediction] = Field(
        ...,
        description="Top predictions, ordered by confidence (highest first).",
    )
    note: Optional[str] = Field(
        default=None,
        description="Optional human-readable note, e.g. fallback reason.",
    )