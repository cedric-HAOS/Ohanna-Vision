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
    """The frontend JavaScript entry point must be served."""
    client = make_client()

    response = client.get("/ui/app.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert 'from "./application.js"' in response.text
    assert "ApplicationController" in response.text
    assert "application.initialize()" in response.text

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

def test_static_ui_exposes_only_functional_navigation_entries() -> None:
    """The sidebar must expose only implemented application views."""
    response = make_client().get("/ui/")

    assert response.status_code == 200

    content = response.text

    assert 'data-navigation-target="overview"' in content
    assert 'data-navigation-target="infrastructure"' in content
    assert 'data-navigation-target="timeline"' in content
    assert 'data-navigation-target="observations"' in content

def test_static_ui_does_not_expose_unimplemented_navigation_entries() -> None:
    """The sidebar must not advertise unavailable application views."""
    response = make_client().get("/ui/")

    assert response.status_code == 200

    content = response.text

    assert 'data-navigation-target="services"' not in content
    assert 'data-navigation-target="alerts"' not in content
    assert 'data-navigation-target="reports"' not in content
    assert 'data-navigation-target="system"' not in content
    assert 'data-navigation-target="settings"' not in content

def test_static_ui_declares_all_navigation_views() -> None:
    """Every navigation destination must have a corresponding view."""
    response = make_client().get("/ui/")

    assert response.status_code == 200

    content = response.text

    assert 'data-view="overview"' in content
    assert 'data-view="infrastructure"' in content
    assert 'data-view="timeline"' in content
    assert 'data-view="observations"' in content

def test_static_ui_loads_navigation_as_javascript_module() -> None:
    """The frontend must load the modular navigation controller."""
    client = make_client()

    page_response = client.get("/ui/")
    navigation_response = client.get("/ui/navigation.js")

    assert page_response.status_code == 200
    assert navigation_response.status_code == 200

    assert 'type="module"' in page_response.text
    assert "export class NavigationController" in navigation_response.text

def test_static_ui_exposes_navigation_controller() -> None:
    """The UI must expose its navigation controller."""
    client = make_client()

    response = client.get("/ui/navigation.js")

    assert response.status_code == 200
    assert "export class NavigationController" in response.text
    assert "ohanna:navigation-changed" in response.text
    assert "hashchange" in response.text

def test_application_script_connects_navigation() -> None:
    """The application must initialize frontend navigation."""
    client = make_client()

    response = client.get("/ui/application.js")

    assert response.status_code == 200
    assert "NavigationController" in response.text
    assert 'from "./navigation.js"' in response.text
    assert '"ohanna:navigation-changed"' in response.text
    assert "this.navigation.initialize()" in response.text

def test_application_reflows_topology_after_navigation() -> None:
    """Opening Infrastructure must reflow its topology."""
    client = make_client()

    application_response = client.get(
        "/ui/application.js",
    )
    topology_response = client.get(
        "/ui/topology.js",
    )

    assert application_response.status_code == 200
    assert topology_response.status_code == 200

    assert (
        'viewName === "infrastructure"'
        in application_response.text
    )
    assert (
        "this.topology.reflow()"
        in application_response.text
    )

    assert (
        "requestAnimationFrame"
        in topology_response.text
    )
    assert (
        'new Event("resize")'
        in topology_response.text
    )

def test_static_ui_exposes_frontend_api_module() -> None:
    """The frontend must expose its API client module."""
    response = make_client().get("/ui/api.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert "export const API" in response.text
    assert 'runtime: "/api/runtime"' in response.text
    assert 'observations: "/api/observations"' in response.text
    assert 'timeline: "/api/timeline"' in response.text
    assert 'topology: "/api/topology"' in response.text
    assert "export async function fetchJson" in response.text

def test_static_ui_exposes_frontend_utils_module() -> None:
    """The frontend must expose shared utility functions."""
    response = make_client().get("/ui/utils.js")

    assert response.status_code == 200
    assert "export function escapeHtml" in response.text
    assert "export function formatDate" in response.text
    assert "export function formatLatency" in response.text
    assert "export function normalizeHealthStatus" in response.text

def test_static_ui_exposes_shared_application_state() -> None:
    """The frontend must expose a shared application state."""
    response = make_client().get(
        "/ui/application_state.js",
    )

    assert response.status_code == 200
    assert "export function applicationState" in response.text
    assert "export function resetApplicationState" in response.text

def test_application_uses_frontend_foundation_modules() -> None:
    """The application orchestrator must import shared modules."""
    response = make_client().get("/ui/application.js")

    assert response.status_code == 200
    assert 'from "./api.js"' in response.text
    assert 'from "./utils.js"' in response.text
    assert 'from "./application_state.js"' in response.text

def test_static_ui_exposes_observations_module() -> None:
    """The frontend must expose its observations module."""
    client = make_client()

    response = client.get("/ui/observations.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert "export class ObservationsController" in response.text
    assert "renderRecent(" in response.text
    assert "renderTable(" in response.text
    assert "renderTableRow(" in response.text

def test_application_uses_observations_controller() -> None:
    """The application must delegate observation rendering."""
    response = make_client().get("/ui/application.js")

    assert response.status_code == 200
    assert "ObservationsController" in response.text
    assert 'from "./observations.js"' in response.text
    assert "this.observations.render(" in response.text
    assert "this.observations.showError(" in response.text

def test_observations_module_uses_shared_frontend_foundations() -> None:
    """The observations module must reuse state and utilities."""
    response = make_client().get(
        "/ui/observations.js",
    )

    assert response.status_code == 200
    assert 'from "./utils.js"' in response.text
    assert "this.state.observations" in response.text
    assert "formatDate" in response.text
    assert "formatLatency" in response.text
    assert "statusBadge" in response.text

def test_static_ui_exposes_timeline_module() -> None:
    """The frontend must expose its timeline module."""
    response = make_client().get(
        "/ui/timeline.js",
    )

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert "export class TimelineController" in response.text
    assert "groupObservationsByNode" in response.text
    assert "timelinePosition" in response.text
    assert "renderAxis" in response.text
    assert "renderRow" in response.text

def test_application_uses_timeline_controller() -> None:
    """The application must delegate timeline rendering."""
    response = make_client().get("/ui/application.js")

    assert response.status_code == 200
    assert "TimelineController" in response.text
    assert 'from "./timeline.js"' in response.text
    assert "this.timeline.initialize()" in response.text
    assert "this.timeline.render()" in response.text

def test_timeline_module_uses_shared_application_state() -> None:
    """The timeline must use observations from shared state."""
    response = make_client().get(
        "/ui/timeline.js",
    )

    assert response.status_code == 200
    assert "this.state.observations" in response.text
    assert "this.state.timelineRangeHours" in response.text
    assert "data-timeline-hours" in response.text

def test_timeline_delegates_node_selection() -> None:
    """Timeline interactions must delegate node selection."""
    response = make_client().get(
        "/ui/timeline.js",
    )

    assert response.status_code == 200
    assert "onNodeSelected" in response.text
    assert "button.dataset.timelineNode" in response.text
    assert "button.dataset.nodeId" in response.text
def test_static_ui_exposes_topology_module() -> None:
    """The frontend must expose its topology module."""
    response = make_client().get(
        "/ui/topology.js",
    )

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert "export class TopologyController" in response.text
    assert "new window.TopologyCanvas" in response.text
    assert "buildDeviceHealth" in response.text
    assert "selectDeviceByNode" in response.text

def test_topology_module_loads_backend_resources() -> None:
    """The topology controller must load topology and timeline data."""
    response = make_client().get(
        "/ui/topology.js",
    )

    assert response.status_code == 200
    assert 'from "./api.js"' in response.text
    assert "fetchJson(API.topology)" in response.text
    assert "fetchJson(API.timeline)" in response.text
    assert "Promise.all" in response.text

def test_topology_module_controls_canvas() -> None:
    """The topology controller must expose canvas controls."""
    response = make_client().get(
        "/ui/topology.js",
    )

    assert response.status_code == 200
    assert "this.canvas.zoomIn()" in response.text
    assert "this.canvas.zoomOut()" in response.text
    assert "this.canvas.resetView()" in response.text
    assert "this.canvas.setSelectedDevice" in response.text

def test_application_uses_topology_controller() -> None:
    """The application must delegate topology management."""
    response = make_client().get("/ui/application.js")

    assert response.status_code == 200
    assert "TopologyController" in response.text
    assert 'from "./topology.js"' in response.text
    assert "this.topology.load()" in response.text
    assert "this.topology.initialize()" in response.text
    assert "this.topology.reflow()" in response.text

def test_static_ui_exposes_device_details_module() -> None:
    """The frontend must expose its device-details module."""
    response = make_client().get(
        "/ui/device_details.js",
    )

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert (
        "export class DeviceDetailsController"
        in response.text
    )
    assert "select(deviceId)" in response.text
    assert "render(device)" in response.text
    assert "renderLinks(device)" in response.text
    assert "close()" in response.text

def test_device_details_module_uses_shared_state() -> None:
    """Device details must use topology state."""
    response = make_client().get(
        "/ui/device_details.js",
    )

    assert response.status_code == 200
    assert "this.state.topology" in response.text
    assert "this.state.deviceHealth" in response.text
    assert "this.state.selectedDeviceId" in response.text

def test_device_details_module_renders_connections() -> None:
    """Device details must render infrastructure links."""
    response = make_client().get(
        "/ui/device_details.js",
    )

    assert response.status_code == 200
    assert "linksForDevice" in response.text
    assert "neighborForLink" in response.text
    assert "device-details__link" in response.text
    assert "source_device_id" in response.text
    assert "target_device_id" in response.text

def test_application_uses_device_details_controller() -> None:
    """The application must delegate device selection."""
    response = make_client().get(
        "/ui/application.js",
    )

    assert response.status_code == 200
    assert "DeviceDetailsController" in response.text
    assert 'from "./device_details.js"' in response.text
    assert "this.deviceDetails.initialize()" in response.text
    assert "this.deviceDetails" in response.text
    assert ".select(" in response.text
    assert ".refresh()" in response.text

def test_static_ui_exposes_dashboard_module() -> None:
    """The frontend must expose its dashboard module."""
    response = make_client().get(
        "/ui/dashboard.js",
    )

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert "export class DashboardController" in response.text
    assert "renderRuntime(runtime)" in response.text
    assert "renderKpis()" in response.text
    assert "renderActiveAlerts()" in response.text
    assert "updateViewHeader(viewName)" in response.text


def test_dashboard_module_calculates_health_kpis() -> None:
    """The dashboard must calculate infrastructure health."""
    response = make_client().get(
        "/ui/dashboard.js",
    )

    assert response.status_code == 200
    assert "deviceHealthStatistics()" in response.text
    assert "globalTopologyHealth(" in response.text
    assert "availabilityPercentage(" in response.text
    assert "formatGlobalTopologyHealth(" in response.text


def test_dashboard_module_renders_runtime_statistics() -> None:
    """The dashboard must render runtime statistics."""
    response = make_client().get(
        "/ui/dashboard.js",
    )

    assert response.status_code == 200
    assert "observations_received" in response.text
    assert "observations_accepted" in response.text
    assert "observations_rejected" in response.text
    assert "renderAcceptanceRate(" in response.text

def test_dashboard_module_delegates_alert_selection() -> None:
    """Active alerts must delegate device selection."""
    response = make_client().get(
        "/ui/dashboard.js",
    )

    assert response.status_code == 200
    assert "onDeviceSelected" in response.text
    assert "data-device-id" in response.text
    assert "button.dataset.deviceId" in response.text

def test_application_uses_dashboard_controller() -> None:
    """The application must delegate dashboard rendering."""
    response = make_client().get(
        "/ui/application.js",
    )

    assert response.status_code == 200
    assert "DashboardController" in response.text
    assert 'from "./dashboard.js"' in response.text
    assert "this.dashboard.renderRuntime(" in response.text
    assert "this.dashboard" in response.text
    assert ".renderKpis()" in response.text
    assert ".renderActiveAlerts()" in response.text

def test_static_ui_exposes_websocket_module() -> None:
    """The frontend must expose its WebSocket module."""
    response = make_client().get(
        "/ui/websocket.js",
    )

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert (
        "export class WebSocketController"
        in response.text
    )
    assert "initialize()" in response.text
    assert "connect()" in response.text
    assert "stop()" in response.text


def test_websocket_module_builds_realtime_url() -> None:
    """The WebSocket module must support HTTP and HTTPS."""
    response = make_client().get(
        "/ui/websocket.js",
    )

    assert response.status_code == 200
    assert "websocketUrl()" in response.text
    assert '"https:"' in response.text
    assert '"wss:"' in response.text
    assert '"ws:"' in response.text
    assert 'window.location.host' in response.text


def test_websocket_module_handles_connection_states() -> None:
    """The WebSocket module must render connection states."""
    response = make_client().get(
        "/ui/websocket.js",
    )

    assert response.status_code == 200
    assert '"connecting"' in response.text
    assert '"online"' in response.text
    assert '"offline"' in response.text
    assert "connection-status" in response.text


def test_websocket_module_reconnects_after_close() -> None:
    """The WebSocket module must reconnect after disconnection."""
    response = make_client().get(
        "/ui/websocket.js",
    )

    assert response.status_code == 200
    assert "scheduleReconnect()" in response.text
    assert "setTimeout" in response.text
    assert "clearTimeout" in response.text
    assert "reconnectDelayMs" in response.text


def test_websocket_module_delegates_messages() -> None:
    """Realtime messages must be delegated to the application."""
    response = make_client().get(
        "/ui/websocket.js",
    )

    assert response.status_code == 200
    assert "JSON.parse(" in response.text
    assert 'message.type === "connected"' in response.text
    assert "this.onMessage(message)" in response.text


def test_application_uses_websocket_controller() -> None:
    """The application must delegate realtime communication."""
    response = make_client().get("/ui/application.js")

    assert response.status_code == 200
    assert "WebSocketController" in response.text
    assert 'from "./websocket.js"' in response.text
    assert "this.websocket.initialize()" in response.text
    assert "void this.refresh()" in response.text

def test_static_ui_exposes_application_module() -> None:
    """The frontend must expose its application orchestrator."""
    response = make_client().get(
        "/ui/application.js",
    )

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert (
        "export class ApplicationController"
        in response.text
    )
    assert "createControllers()" in response.text
    assert "initializeControllers()" in response.text
    assert "async refresh()" in response.text

def test_application_module_coordinates_frontend_controllers() -> None:
    """The application must coordinate all frontend controllers."""
    response = make_client().get(
        "/ui/application.js",
    )

    assert response.status_code == 200

    assert "DashboardController" in response.text
    assert "DeviceDetailsController" in response.text
    assert "NavigationController" in response.text
    assert "ObservationsController" in response.text
    assert "TimelineController" in response.text
    assert "TopologyController" in response.text
    assert "WebSocketController" in response.text

def test_application_module_refreshes_backend_resources() -> None:
    """The application must refresh its backend-backed state."""
    response = make_client().get(
        "/ui/application.js",
    )

    assert response.status_code == 200
    assert "this.loadRuntime()" in response.text
    assert "this.loadObservations()" in response.text
    assert "this.topology.load()" in response.text
    assert "Promise.allSettled" in response.text

def test_application_entry_point_is_minimal() -> None:
    """The frontend entry point must only start the application."""
    response = make_client().get("/ui/app.js")

    assert response.status_code == 200
    assert 'from "./application.js"' in response.text
    assert "new ApplicationController()" in response.text
    assert "application.initialize()" in response.text

    assert "fetchJson(" not in response.text
    assert "new WebSocket(" not in response.text
    assert "new TopologyController(" not in response.text
    assert "renderKpis(" not in response.text