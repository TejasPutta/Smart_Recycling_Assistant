"""
Integration tests for /api/v1/classify and /api/v1/classify/status.

These hit the real FastAPI app through TestClient and exercise:
- Successful classification of a valid image
- Rejection of non-image uploads
- Rejection of empty uploads
- Status endpoint shape

They do NOT require the ML model to be loaded — the demo fallback is a
valid response and is exercised automatically when torch weights are
not available in the test environment.
"""

from io import BytesIO

import pytest
from fastapi.testclient import TestClient
from PIL import Image


def _png_bytes(size: tuple[int, int] = (64, 64), color=(120, 120, 120)) -> bytes:
    """Return bytes of a tiny valid PNG."""
    buf = BytesIO()
    Image.new("RGB", size, color=color).save(buf, format="PNG")
    return buf.getvalue()


def test_classify_accepts_valid_png(client: TestClient) -> None:
    files = {"file": ("test.png", _png_bytes(), "image/png")}
    response = client.post("/api/v1/classify", files=files)
    assert response.status_code == 200, response.text
    body = response.json()

    assert body["source"] in {"model", "demo"}
    assert isinstance(body["predictions"], list)
    assert len(body["predictions"]) >= 1

    top = body["predictions"][0]
    assert "label" in top
    assert "category" in top
    assert 0.0 <= float(top["confidence"]) <= 1.0
    assert "category_info" in top
    assert "display_name" in top["category_info"]
    assert "recyclability" in top["category_info"]


def test_classify_accepts_valid_jpeg(client: TestClient) -> None:
    buf = BytesIO()
    Image.new("RGB", (80, 60), color=(200, 60, 60)).save(buf, format="JPEG")
    files = {"file": ("test.jpg", buf.getvalue(), "image/jpeg")}
    response = client.post("/api/v1/classify", files=files)
    assert response.status_code == 200, response.text


def test_classify_rejects_non_image_bytes(client: TestClient) -> None:
    # Send plain text with a fake image/png content type
    files = {"file": ("fake.png", b"this is not an image", "image/png")}
    response = client.post("/api/v1/classify", files=files)
    assert response.status_code == 400
    assert "valid" in response.json()["detail"].lower() or "image" in response.json()["detail"].lower()


def test_classify_rejects_empty_upload(client: TestClient) -> None:
    files = {"file": ("empty.png", b"", "image/png")}
    response = client.post("/api/v1/classify", files=files)
    assert response.status_code == 400


def test_classify_rejects_wrong_content_type(client: TestClient) -> None:
    files = {"file": ("notes.txt", b"hello", "text/plain")}
    response = client.post("/api/v1/classify", files=files)
    assert response.status_code == 415


def test_classify_status_endpoint(client: TestClient) -> None:
    response = client.get("/api/v1/classify/status")
    assert response.status_code == 200
    body = response.json()
    assert "model_available" in body
    assert isinstance(body["model_available"], bool)