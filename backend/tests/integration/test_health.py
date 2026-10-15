"""Integration tests for health and root endpoints."""

from fastapi.testclient import TestClient


def test_health_returns_ok(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "ok"
    assert body["service"] == "Smart Recycling Assistant API"
    assert body["version"] == "0.1.0"
    assert "timestamp" in body


def test_health_content_type_is_json(client: TestClient) -> None:
    response = client.get("/api/v1/health")
    assert response.headers["content-type"].startswith("application/json")


def test_root_endpoint_returns_service_info(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["service"] == "Smart Recycling Assistant API"
    assert body["health"] == "/api/v1/health"
    assert body["docs"] == "/docs"


def test_openapi_schema_is_available(client: TestClient) -> None:
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Smart Recycling Assistant API"
    assert "/api/v1/health" in schema["paths"]