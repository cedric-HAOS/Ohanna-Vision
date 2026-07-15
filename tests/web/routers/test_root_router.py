"""Tests for the root web router."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ohanna_vision.web.routers import root_router


def make_client() -> TestClient:
    """Create a test client containing only the root router."""
    app = FastAPI()
    app.include_router(root_router)

    return TestClient(app)


def test_root_router_exposes_application_status() -> None:
    """The root router must expose the application status."""
    client = make_client()

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Ohanna Vision",
        "status": "running",
    }
