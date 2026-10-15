"""Waste classifier service — zero-shot with CLIP."""

from __future__ import annotations

import logging
import threading
from typing import Optional

from PIL import Image
from torch import no_grad

from app.schemas.classification import (
    ClassificationPrediction,
    ClassificationSource,
    WasteCategory,
)
from app.services.classification.category_mapper import all_category_infos

logger = logging.getLogger(__name__)

MODEL_NAME = "clip_vit_base_patch32_zeroshot"
DEFAULT_TOP_K = 3

CATEGORY_PROMPTS = {
    WasteCategory.BATTERY:        "a battery or power bank",
    WasteCategory.HAZARDOUS:      "a syringe, aerosol can, light bulb, or electronic circuit",
    WasteCategory.CHEMICAL:       "a chemical container, detergent, paint, or motor oil bottle",
    WasteCategory.PLASTIC:        "a plastic bottle, bag, or container",
    WasteCategory.PAPER:          "paper, newspaper, cardboard, or magazine",
    WasteCategory.FABRIC:         "clothing, textile, shoe, or fabric",
    WasteCategory.BIODEGRADABLE:  "food scraps, fruit, vegetable, or leaves",
    WasteCategory.OTHER:          "general trash or an unknown object",
}

_CATEGORY_INFO_CACHE = {info.category: info for info in all_category_infos()}

_model = None
_processor = None
_load_error: Optional[str] = None
_load_lock = threading.Lock()


def _load_model_once() -> None:
    global _model, _processor, _load_error
    if _model is not None or _load_error is not None:
        return
    with _load_lock:
        if _model is not None or _load_error is not None:
            return
        try:
            from transformers import CLIPModel, CLIPProcessor
            _processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            _model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
            _model.eval()
            logger.info("Loaded classifier: %s", MODEL_NAME)
        except Exception as exc:
            _load_error = f"{type(exc).__name__}: {exc}"
            logger.warning("Classifier unavailable: %s", _load_error)


def is_model_available() -> bool:
    _load_model_once()
    return _model is not None


def get_load_error() -> Optional[str]:
    _load_model_once()
    return _load_error


def _demo_predictions():
    info = _CATEGORY_INFO_CACHE[WasteCategory.OTHER]
    return [ClassificationPrediction(
        label="unknown (model not loaded)",
        category=info.category,
        confidence=0.0,
        category_info=info,
    )]


def classify_image(image: Image.Image, top_k: int = DEFAULT_TOP_K):
    _load_model_once()

    if _model is None or _processor is None:
        note = "Classifier unavailable; demo result."
        if _load_error:
            note = f"{note} Reason: {_load_error}"
        return _demo_predictions(), ClassificationSource.DEMO, note

    categories = list(CATEGORY_PROMPTS.keys())
    prompts = [CATEGORY_PROMPTS[c] for c in categories]

    inputs = _processor(
        text=prompts,
        images=image.convert("RGB"),
        return_tensors="pt",
        padding=True,
    )
    with no_grad():
        probs = _model(**inputs).logits_per_image.softmax(dim=1)[0]

    k = min(top_k, len(categories))
    top_probs, top_idx = probs.topk(k)

    predictions = []
    for prob, idx in zip(top_probs.tolist(), top_idx.tolist()):
        category = categories[int(idx)]
        info = _CATEGORY_INFO_CACHE[category]
        predictions.append(ClassificationPrediction(
            label=info.display_name,
            category=category,
            confidence=round(float(prob), 4),
            category_info=info,
        ))
    return predictions, ClassificationSource.MODEL, None