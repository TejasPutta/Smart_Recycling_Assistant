"""
Image validation utilities.

Rejects bad uploads before they reach the ML classifier:
- Unsupported MIME types
- Files larger than the configured limit
- Non-decodable image bytes
- Images with suspicious dimensions

Returns a normalized RGB PIL Image ready for the model.
"""

from io import BytesIO

from fastapi import HTTPException, UploadFile, status
from PIL import Image, UnidentifiedImageError

from app.core.config import get_settings

# Absolute safety caps (independent of user config)
_ABSOLUTE_MAX_BYTES = 20 * 1024 * 1024  # 20 MB hard ceiling
_MAX_DIMENSION = 8000  # px — reject absurd images


def _read_upload_bytes(upload: UploadFile, max_bytes: int) -> bytes:
    """Read upload bytes with a hard size cap."""
    upload.file.seek(0)
    data = upload.file.read(max_bytes + 1)
    if len(data) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Image exceeds maximum size of {max_bytes // (1024 * 1024)} MB.",
        )
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty upload — no image bytes received.",
        )
    return data


def validate_image_upload(upload: UploadFile) -> Image.Image:
    """
    Validate an UploadFile and return a normalized RGB PIL Image.

    Raises HTTPException on any validation failure.
    """
    settings = get_settings()

    # 1. Content-type check (advisory; browsers sometimes lie, so we double-check by decoding)
    if upload.content_type and upload.content_type not in settings.allowed_image_types:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail=(
                f"Unsupported content type '{upload.content_type}'. "
                f"Allowed: {', '.join(settings.allowed_image_types)}."
            ),
        )

    # 2. Size check (respect both user config and absolute cap)
    max_bytes = min(
        settings.max_upload_size_mb * 1024 * 1024,
        _ABSOLUTE_MAX_BYTES,
    )
    data = _read_upload_bytes(upload, max_bytes)

    # 3. Decode check (this catches fake .jpg files that are actually text)
    try:
        with Image.open(BytesIO(data)) as img:
            img.verify()  # detects corruption
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is not a valid or supported image.",
        ) from exc

    # 4. Reopen for use (verify() consumes the file)
    try:
        image = Image.open(BytesIO(data))
        image.load()
    except (UnidentifiedImageError, OSError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded image could not be loaded.",
        ) from exc

    # 5. Dimension sanity check
    width, height = image.size
    if width == 0 or height == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Image has zero width or height.",
        )
    if max(width, height) > _MAX_DIMENSION:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Image dimension exceeds {_MAX_DIMENSION}px.",
        )

    # 6. Normalize to RGB (drop alpha / palette / grayscale)
    return image.convert("RGB")