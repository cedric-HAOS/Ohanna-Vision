"""Tests for the Ohanna-Vision FastAPI application."""

from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ohanna_vision.domain.observation_store import ObservationStore
from ohanna_vision.runtime import BackendRuntime
from ohanna_vision.timeline import TimelineEngine
from ohanna_vision.web import ApplicationContext, WebSocketHub, create_app


def test_create_app_returns_fastapi_application() -> None:
    """The application factory must return a FastAPI instance."""
    app = create_app()

    assert isinstance(app, FastAPI)

def test_root_endpoint_returns_application_status() -> None:
    """The application must expose its root status endpoint."""
    client = TestClient(create_app())

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Ohanna Vision",
        "status": "running",
    }


def test_api_endpoint_returns_api_status() -> None:
    """The application must expose the API router."""
    client = TestClient(create_app())

    response = client.get("/api/")

    assert response.status_code == 200
    assert response.json() == {
        "name": "Ohanna Vision API",
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

def make_context() -> ApplicationContext:
    """Create a context for application factory tests."""
    return ApplicationContext(
        runtime=cast(BackendRuntime, object()),
        observation_store=cast(ObservationStore, object()),
        timeline_engine=cast(TimelineEngine, object()),
    )


def test_create_app_accepts_application_context() -> None:
    """The application factory must accept a service context."""
    context = make_context()

    app = create_app(context)

    assert app.state.context is context


def test_create_app_can_run_without_application_context() -> None:
    """The basic web application must remain independently runnable."""
    app = create_app()

    assert getattr(app.state, "context", None) is None

def test_runtime_api_is_registered() -> None:
    """The application must register the runtime API."""
    client = TestClient(create_app())

    response = client.get("/api/runtime")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Application context is not configured",
    }

def test_runtime_api_is_exposed_in_openapi() -> None:
    """The runtime API must appear in the OpenAPI schema."""
    client = TestClient(create_app())

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/runtime" in response.json()["paths"]

def test_observations_api_is_registered() -> None:
    """The application must register the observation API."""
    client = TestClient(create_app())

    response = client.get("/api/observations")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Application context is not configured",
    }


def test_observations_api_is_exposed_in_openapi() -> None:
    """The observation API must appear in the OpenAPI schema."""
    client = TestClient(create_app())

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/observations" in response.json()["paths"]

def test_timeline_api_is_registered() -> None:
    """The application must register the timeline API."""
    client = TestClient(create_app())

    response = client.get("/api/timeline")

    assert response.status_code == 503

def test_timeline_routes_are_exposed_in_openapi() -> None:
    """Timeline routes must appear in the OpenAPI schema."""
    response = TestClient(create_app()).get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/api/timeline" in paths
    assert "/api/timeline/nodes/{node_id}" in paths
    assert (
        "/api/timeline/nodes/{node_id}/services/{service_id}"
        in paths
    )

def test_create_app_stores_websocket_hub() -> None:
    """The application must retain its WebSocket hub."""
    hub = WebSocketHub()

    app = create_app(websocket_hub=hub)

    assert app.state.websocket_hub is hub

def test_create_app_builds_default_websocket_hub() -> None:
    """The application must build a hub when none is provided."""
    app = create_app()

    assert isinstance(
        app.state.websocket_hub,
        WebSocketHub,
    )

def test_application_mounts_static_ui() -> None:
    """The application must expose the static dashboard."""
    client = TestClient(create_app())

    response = client.get("/ui/")

    assert response.status_code == 200

def test_observation_ingestion_is_exposed_in_openapi() -> None:
    """The ingestion endpoint must appear in the OpenAPI schema."""
    response = TestClient(create_app()).get("/openapi.json")

    assert response.status_code == 200
    assert "post" in response.json()["paths"]["/api/observations"]