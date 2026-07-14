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
    assert 'id="overview"' in response.text
    assert 'id="infrastructure"' in response.text
    assert 'id="topology-heading"' in response.text
    assert 'id="observations"' in response.text
    assert 'id="timeline"' in response.text
    assert 'id="timeline-heading"' in response.text

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
    assert 'topology: "/api/topology"' in response.text


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

def test_static_ui_contains_topology_canvas_container() -> None:
    """The dashboard must expose the topology canvas container."""
    client = make_client()

    response = client.get("/ui/")

    assert response.status_code == 200
    assert 'id="topology-container"' in response.text
    assert 'id="topology-layout-label"' in response.text
    assert 'id="topology-error"' in response.text

def test_topology_canvas_javascript_is_available() -> None:
    """The topology canvas component must be served."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert "class TopologyCanvas" in response.text
    assert "window.TopologyCanvas" in response.text

def test_static_ui_contains_device_details_panel() -> None:
    """The dashboard must expose the device details panel."""
    client = make_client()

    response = client.get("/ui/")

    assert response.status_code == 200
    assert 'id="device-details"' in response.text
    assert 'id="device-details-title"' in response.text
    assert 'id="device-details-close"' in response.text
    assert 'id="device-links-list"' in response.text

def test_static_ui_contains_topology_controls() -> None:
    """The dashboard must expose topology navigation controls."""
    client = make_client()

    response = client.get("/ui/")

    assert response.status_code == 200
    assert 'id="topology-zoom-in"' in response.text
    assert 'id="topology-zoom-out"' in response.text
    assert 'id="topology-reset-view"' in response.text

def test_static_ui_contains_dashboard_grid() -> None:
    """The dashboard must expose its new general layout."""
    client = make_client()

    response = client.get("/ui/")

    assert response.status_code == 200
    assert 'class="application-sidebar"' in response.text
    assert 'class="dashboard-header"' in response.text
    assert 'class="dashboard-kpis"' in response.text
    assert "dashboard-primary" in response.text
    assert "dashboard-primary--topology" in response.text
    assert 'class="dashboard-right-panel"' in response.text
    assert 'class="dashboard-timeline"' in response.text

def test_static_ui_preserves_interactive_components() -> None:
    """The new layout must preserve existing dashboard components."""
    client = make_client()

    response = client.get("/ui/")

    assert response.status_code == 200
    assert 'id="websocket-status"' in response.text
    assert 'id="topology-container"' in response.text
    assert 'id="device-details"' in response.text
    assert 'id="topology-zoom-in"' in response.text
    assert 'id="observations-body"' in response.text

def test_static_ui_contains_dashboard_kpis() -> None:
    """The dashboard must expose its main KPI cards."""
    client = make_client()

    response = client.get("/ui/")

    assert response.status_code == 200
    assert 'id="availability-value"' in response.text
    assert 'id="devices-count"' in response.text
    assert 'id="services-count"' in response.text
    assert 'id="capabilities-count"' in response.text
    assert 'id="alerts-count"' in response.text
    assert 'id="activity-count"' in response.text

def test_static_ui_marks_topology_as_primary_content() -> None:
    """The topology must be the primary dashboard content."""
    client = make_client()

    response = client.get("/ui/")

    assert response.status_code == 200
    assert "dashboard-primary--topology" in response.text
    assert 'id="topology-health-indicator"' in response.text
    assert 'id="topology-health-label"' in response.text
    assert "Topologie Ohanna-House" in response.text

def test_static_ui_contains_realtime_side_panel() -> None:
    """The dashboard must expose its realtime side panel."""
    client = make_client()

    response = client.get("/ui/")

    assert response.status_code == 200
    assert 'id="active-alerts-count"' in response.text
    assert 'id="active-alerts-list"' in response.text
    assert 'id="recent-observations-list"' in response.text
    assert 'id="acceptance-rate"' in response.text
    assert 'id="acceptance-rate-progress"' in response.text

def test_static_ui_contains_graphical_timeline() -> None:
    """The dashboard must expose its graphical timeline."""
    client = make_client()

    response = client.get("/ui/")

    assert response.status_code == 200
    assert 'id="timeline-content"' in response.text
    assert 'id="timeline-event-count"' in response.text
    assert 'data-timeline-hours="1"' in response.text
    assert 'data-timeline-hours="6"' in response.text
    assert 'data-timeline-hours="24"' in response.text

def test_static_styles_support_responsive_dashboard() -> None:
    """The dashboard stylesheet must expose responsive rules."""
    client = make_client()

    response = client.get("/ui/styles.css")

    assert response.status_code == 200
    assert "@media (max-width: 1200px)" in response.text
    assert "@media (max-width: 1000px)" in response.text
    assert "@media (max-width: 720px)" in response.text
    assert "@media (max-width: 460px)" in response.text

def test_static_styles_respect_reduced_motion() -> None:
    """The dashboard must respect reduced-motion preferences."""
    client = make_client()

    response = client.get("/ui/styles.css")

    assert response.status_code == 200
    assert (
        "@media (prefers-reduced-motion: reduce)"
        in response.text
    )