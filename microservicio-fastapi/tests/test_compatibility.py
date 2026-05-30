from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _payload(vector_a, vector_b):
    return {"vector_a": {"vector": vector_a}, "vector_b": {"vector": vector_b}}


def test_health_ok():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_calculate_compatible():
    response = client.post("/compatibility/calculate", json=_payload([1, 2, 3], [1, 2, 3]))
    assert response.status_code == 200
    body = response.json()
    assert body["score"] == pytest.approx(1.0)
    assert body["classification"] == "COMPATIBLE"
    assert body["score_percentage"] == pytest.approx(100.0)


def test_calculate_not_compatible():
    response = client.post("/compatibility/calculate", json=_payload([1, 0], [-1, 0]))
    assert response.status_code == 200
    assert response.json()["classification"] == "NOT_COMPATIBLE"


def test_calculate_mismatched_dimensions_returns_422():
    response = client.post("/compatibility/calculate", json=_payload([1, 2], [1, 2, 3]))
    assert response.status_code == 422


def test_calculate_empty_vector_returns_422():
    response = client.post("/compatibility/calculate", json=_payload([], [1]))
    assert response.status_code == 422


def test_calculate_missing_field_returns_422():
    response = client.post("/compatibility/calculate", json={"vector_a": {"vector": [1, 2]}})
    assert response.status_code == 422
