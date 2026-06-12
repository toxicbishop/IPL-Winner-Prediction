"""API-level tests for server.py: input validation + CORS."""

import pytest
from fastapi.testclient import TestClient

import server


@pytest.fixture()
def client():
    return TestClient(server.app)


@pytest.mark.parametrize(
    "endpoint",
    [
        "/api/winner-probabilities",
        "/api/model-performance",
        "/api/match-fixtures",
        "/api/intelligence",
    ],
)
def test_rejects_bad_tournament(client, endpoint):
    r = client.get(endpoint, params={"tournament": "../etc/passwd"})
    assert r.status_code == 400
    assert "Invalid tournament" in r.json()["detail"]


def test_shap_rejects_bad_model_name(client):
    r = client.get("/api/shap-importance/evil;rm", params={"tournament": "ipl"})
    assert r.status_code == 400
    assert "Invalid model" in r.json()["detail"]


def test_shap_rejects_bad_tournament(client):
    r = client.get("/api/shap-importance/random_forest", params={"tournament": "bogus"})
    assert r.status_code == 400


def test_valid_tournament_returns_200(client):
    r = client.get("/api/winner-probabilities", params={"tournament": "ipl"})
    assert r.status_code == 200
    # Either real results or the "not found" sentinel — both are JSON objects.
    assert isinstance(r.json(), dict)


def test_cors_blocks_unknown_origin(client):
    r = client.options(
        "/api/winner-probabilities",
        headers={
            "Origin": "https://evil.example.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    # Starlette returns 400 for disallowed origins on preflight
    assert (
        "access-control-allow-origin" not in {k.lower() for k in r.headers.keys()}
        or r.headers.get("access-control-allow-origin") != "https://evil.example.com"
    )


def test_cors_allows_configured_origin(client):
    r = client.options(
        "/api/winner-probabilities",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert r.headers.get("access-control-allow-origin") == "http://localhost:3000"
