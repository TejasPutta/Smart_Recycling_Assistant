"""Integration tests for /api/v1/statistics and /api/v1/bins."""

from fastapi.testclient import TestClient


def test_statistics_empty_db(client: TestClient) -> None:
    response = client.get("/api/v1/statistics")
    assert response.status_code == 200, response.text
    body = response.json()
    assert "total_scans" in body
    assert isinstance(body["total_scans"], int)
    assert isinstance(body["categories"], list)
    assert isinstance(body["recent"], list)


def test_bins_returns_all_categories(client: TestClient) -> None:
    response = client.get("/api/v1/bins")
    assert response.status_code == 200, response.text
    body = response.json()
    assert "bins" in body
    assert isinstance(body["bins"], list)
    assert len(body["bins"]) == 8  # one per waste category
    for b in body["bins"]:
        assert "category" in b
        assert "fill_percentage" in b
        assert "estimated_items" in b
        assert "status" in b
        assert 0.0 <= b["fill_percentage"] <= 100.0
    assert "note" in body
    assert "virtual" in body["note"].lower()