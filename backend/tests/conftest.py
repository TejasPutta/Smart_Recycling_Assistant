"""Pytest fixtures shared across unit and integration tests."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client() -> TestClient:
    """Return a FastAPI TestClient bound to the real app instance."""
    with TestClient(app) as test_client:
        yield test_client