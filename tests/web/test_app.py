"""Tests for the Ohanna-Vision FastAPI application."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ohanna_vision.web import create_app


def test_create_app_returns_fastapi_application() -> None:
    """The application factory must return a FastAPI instance."""
    app = create_app()

    assert isinstance(app, FastAPI)


def test_root_endpoint_returns_application_status() -> None:
    """The root endpoint must expose the application status."""
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Ohanna Vision",
        "status": "running",
    }


def test_openapi_schema_is_available() -> None:
    """The OpenAPI schema must be exposed."""
    client = TestClient(create_app())

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert response.json()["info"] == {
        "title": "Ohanna Vision",
        "version": "0.1.0",
    }


def test_swagger_documentation_is_available() -> None:
    """Swagger UI must be exposed."""
    client = TestClient(create_app())

    response = client.get("/docs")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]