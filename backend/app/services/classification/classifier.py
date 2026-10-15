"""
Waste classifier service.

Wraps a real pretrained image classifier (MobileNetV3-Large on ImageNet)
and maps its output labels to our normalized waste categories.

Key properties:
- Model is loaded once per process (module-level lazy singleton).
- Weights are downloaded on first use into the PyTorch cache (~/.cache/torch).
- If the model cannot be loaded, we return a clearly-labeled DEMO result
  rather than silently faking a prediction.
- Thread-safe enough for FastAPI's default worker model.
"""

from __future__ import annotations

import logging
import threading
from typing import Optional

from PIL import Image
from torch import Tensor, no_grad
from torchvision.models import MobileNet_V3_Large_Weights, mobilenet_v3_large

from app.schemas.classification import (
    ClassificationPrediction,
    ClassificationSource,
    WasteCategory,
)
from app.services.classification.category_mapper import map_label_to_category

logger = logging.getLogger(__name__)

MODEL_NAME = "mobilenet_v3_large_imagenet"
DEFAULT_TOP_K = 3

_model = None
_weights = None
_load_error: Optional[str] = None
_load_lock = threading.Lock()


def _build_transform(weights: MobileNet_V3_Large_Weights):
    """
    Return the preprocessing pipeline that matches the given pretrained weights.

    torchvision's `weights.transforms()` bundles Resize, CenterCrop, ToTensor,
    and Normalize with the correct mean/std for that specific checkpoint.
    """
    return weights.transforms()

def _load_model_once() -> None:
    """Lazy, thread-safe, one-time model load. Stores error if it fails."""
    global _model, _weights, _load_error
    if _model is not None or _load_error is not None:
        return

    with _load_lock:
        if _model is not None or _load_error is not None:
            return
        try:
            _weights = MobileNet_V3_Large_Weights.IMAGENET1K_V2
            _model = mobilenet_v3_large(weights=_weights)
            _model.eval()
            logger.info("Loaded classifier: %s", MODEL_NAME)
        except Exception as exc:  # pragma: no cover - depends on environment
            _load_error = f"{type(exc).__name__}: {exc}"
            logger.warning("Classifier unavailable, demo mode: %s", _load_error)


def is_model_available() -> bool:
    """True if the real model can be used right now."""
    _load_model_once()
    return _model is not None


def get_load_error() -> Optional[str]:
    """Return the load error message if any (for diagnostics)."""
    _load_model_once()
    return _load_error


def _demo_predictions() -> list[ClassificationPrediction]:
    """
    Honest fallback: return a single 'other' prediction labeled low-confidence.

    This does NOT guess. It clearly says "we don't know" and the API marks
    the response source as DEMO.
    """
    info = map_label_to_category("")  # -> 'other' info
    return [
        ClassificationPrediction(
            label="unknown (model not loaded)",
            category=info.category,
            confidence=0.0,
            category_info=info,
        )
    ]


def classify_image(
    image: Image.Image,
    top_k: int = DEFAULT_TOP_K,
) -> tuple[list[ClassificationPrediction], ClassificationSource, Optional[str]]:
    """
    Run inference on a PIL image.

    Returns:
        (predictions, source, note)
        - predictions: list of ClassificationPrediction, highest confidence first
        - source: ClassificationSource.MODEL or .DEMO
        - note: extra context (e.g. demo reason), else None
    """
    _load_model_once()

    if _model is None:
        note = "Classifier unavailable on this machine; returning demo result."
        if _load_error:
            note = f"{note} Reason: {_load_error}"
        return _demo_predictions(), ClassificationSource.DEMO, note

    transform = _build_transform(_weights)
    tensor: Tensor = transform(image).unsqueeze(0)  # add batch dim

    with no_grad():
        logits = _model(tensor)
        probs = logits.softmax(dim=-1)[0]

    top_probs, top_idx = probs.topk(min(top_k, probs.shape[0]))
    categories = _weights.meta["categories"]

    predictions: list[ClassificationPrediction] = []
    for prob, idx in zip(top_probs.tolist(), top_idx.tolist()):
        raw_label = categories[idx]
        category_info = map_label_to_category(raw_label)
        predictions.append(
            ClassificationPrediction(
                label=raw_label,
                category=category_info.category,
                confidence=round(float(prob), 4),
                category_info=category_info,
            )
        )

    return predictions, ClassificationSource.MODEL, None