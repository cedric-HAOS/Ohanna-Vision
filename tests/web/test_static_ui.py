"""Tests for the Ohanna-Vision static web interface."""

from fastapi.testclient import TestClient

from ohanna_vision.web import create_app


def make_client() -> TestClient:
    """Create an Ohanna-Vision application client."""
    return TestClient(create_app())


def test_static_ui_is_available() -> None:
    """The dashboard entry point must be served."""
    client = make_client()

    response = client.get("/ui/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "<title>Ohanna Vision</title>" in response.text


def test_static_ui_contains_dashboard_sections() -> None:
    """The dashboard must expose its main sections."""
    client = make_client()

    response = client.get("/ui/")

    assert response.status_code == 200
    assert 'id="runtime-heading"' in response.text
    assert 'id="statistics-heading"' in response.text
    assert 'id="infrastructure-heading"' in response.text
    assert 'id="observations-heading"' in response.text


def test_static_styles_are_available() -> None:
    """The dashboard stylesheet must be served."""
    client = make_client()

    response = client.get("/ui/styles.css")

    assert response.status_code == 200
    assert "text/css" in response.headers["content-type"]
    assert ".dashboard" in response.text


def test_static_javascript_is_available() -> None:
    """The dashboard JavaScript must be served."""
    client = make_client()

    response = client.get("/ui/app.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert 'runtime: "/api/runtime"' in response.text
    assert 'observations: "/api/observations"' in response.text
    assert 'timeline: "/api/timeline"' in response.text


def test_static_ui_references_local_assets() -> None:
    """The entry page must reference locally served assets."""
    client = make_client()

    response = client.get("/ui/")

    assert response.status_code == 200
    assert 'href="/ui/styles.css"' in response.text
    assert 'src="/ui/app.js"' in response.text


def test_static_ui_unknown_asset_returns_404() -> None:
    """Unknown static resources must return HTTP 404."""
    client = make_client()

    response = client.get("/ui/unknown.js")

    assert response.status_code == 404