"""Tests for the root web router."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ohana_vision.web.routers import root_router


def make_client() -> TestClient:
    """Create a test client containing only the root router."""
    app = FastAPI()
    app.include_router(root_router)

    return TestClient(app)


def test_root_router_redirects_to_web_interface() -> None:
    """The application root must open the web interface."""
    client = make_client()

    response = client.get(
        "/",
        follow_redirects=False,
    )

    assert response.status_code == 307
    assert response.headers["location"] == "/ui/"
