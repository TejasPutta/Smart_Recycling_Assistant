"""
POST /api/v1/classify — classify a single uploaded waste image.
"""

from fastapi import APIRouter, File, HTTPException, UploadFile, status

from app.schemas.classification import ClassificationResponse
from app.services.classification.classifier import (
    DEFAULT_TOP_K,
    classify_image,
    is_model_available,
)
from app.utils.image_validation import validate_image_upload

router = APIRouter(tags=["Classification"])


@router.post(
    "/classify",
    response_model=ClassificationResponse,
    summary="Classify a waste image",
    description=(
        "Accepts a single image upload, validates it, and returns the "
        "top predicted labels mapped to normalized waste categories. "
        "If no real model is available, returns a clearly-labeled demo "
        "response instead of a fabricated prediction."
    ),
    responses={
        200: {"description": "Classification result"},
        400: {"description": "Invalid image or empty upload"},
        413: {"description": "Image exceeds maximum allowed size"},
        415: {"description": "Unsupported image MIME type"},
    },
)
async def classify(
    file: UploadFile = File(..., description="Image file (JPEG/PNG/WebP)"),
) -> ClassificationResponse:
    image = validate_image_upload(file)

    predictions, source, note = classify_image(image, top_k=DEFAULT_TOP_K)

    if not predictions:
        # Should never happen, but guard anyway.
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Classifier returned no predictions.",
        )

    return ClassificationResponse(
        source=source,
        model_name="mobilenet_v3_large_imagenet" if is_model_available() else None,
        predictions=predictions,
        note=note,
    )


@router.get(
    "/classify/status",
    summary="Classifier availability status",
    description=(
        "Reports whether the real ML model is loaded and ready. "
        "Useful for the frontend to show an 'AI offline — demo mode' banner."
    ),
    tags=["Classification"],
)
async def classifier_status() -> dict:
    return {
        "model_available": is_model_available(),
    }