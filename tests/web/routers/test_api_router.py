"""Tests for the Ohanna-Vision API router."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ohanna_vision.web.routers import api_router


def make_client() -> TestClient:
    """Create a test client containing only the API router."""
    app = FastAPI()
    app.include_router(api_router)

    return TestClient(app)


def test_api_router_uses_api_prefix() -> None:
    """The API router must be exposed below the /api prefix."""
    client = make_client()

    response = client.get("/api/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Ohanna Vision API",
        "status": "running",
    }


def test_api_router_is_not_exposed_without_prefix() -> None:
    """The API route must not be exposed at the application root."""
    client = make_client()

    response = client.get("/")

    assert response.status_code == 404
