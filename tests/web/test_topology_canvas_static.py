"""Tests for the static topology canvas component."""

from fastapi.testclient import TestClient

from ohanna_vision.web import create_app


def make_client() -> TestClient:
    """Create an Ohanna-Vision application client."""
    return TestClient(create_app())


def test_topology_canvas_uses_svg() -> None:
    """The topology canvas must render an SVG document."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert '"http://www.w3.org/2000/svg"' in response.text
    assert '"svg"' in response.text


def test_topology_canvas_renders_curved_links() -> None:
    """The topology canvas must render curved topology links."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "renderLinks(" in response.text
    assert "createLink(" in response.text
    assert "linkCoordinates(" in response.text
    assert '"path"' in response.text


def test_topology_canvas_renders_devices() -> None:
    """The topology canvas must render topology devices."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "renderDevices(" in response.text
    assert "createDevice(" in response.text
    assert '"rect"' in response.text


def test_topology_canvas_prefers_physical_layout() -> None:
    """The topology canvas must prefer the physical layout."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert 'layout.kind === "physical"' in response.text


def test_topology_canvas_skips_unpositioned_elements() -> None:
    """Elements without layout positions must be safely ignored."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "if (!sourcePosition || !targetPosition)" in response.text
    assert "if (!position)" in response.text


def test_topology_canvas_renders_device_icons() -> None:
    """The topology canvas must render icons by device kind."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "createDeviceIcon(" in response.text
    assert "createInternetIcon(" in response.text
    assert "createRouterIcon(" in response.text
    assert "createSwitchIcon(" in response.text
    assert "createAccessPointIcon(" in response.text
    assert "createHomeIcon(" in response.text
    assert "createComputerIcon(" in response.text


def test_topology_canvas_renders_link_labels() -> None:
    """Topology links must expose visual labels."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "createLinkLabel(" in response.text
    assert "linkLabel(" in response.text
    assert "formatBandwidth(" in response.text


def test_topology_canvas_uses_device_metadata() -> None:
    """Device cards must use topology metadata for details."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "device.metadata?.model" in response.text
    assert "device.metadata?.role" in response.text


def test_topology_canvas_applies_device_health() -> None:
    """The topology canvas must apply health to device cards."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "deviceStatus(" in response.text
    assert "normalizeHealthStatus(" in response.text
    assert "createHealthIndicator(" in response.text
    assert "topology-device--health-" in response.text


def test_topology_canvas_applies_link_health() -> None:
    """The topology canvas must derive health for links."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "linkHealth(" in response.text
    assert "topology-link--health-" in response.text


def test_topology_canvas_supports_domain_health_statuses() -> None:
    """The canvas must support every domain health status."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert '"healthy"' in response.text
    assert '"degraded"' in response.text
    assert '"unhealthy"' in response.text
    assert '"unknown"' in response.text


def test_topology_canvas_supports_device_selection() -> None:
    """Topology devices must support pointer selection."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "onDeviceSelected" in response.text
    assert "selectDevice(" in response.text
    assert "setSelectedDevice(" in response.text
    assert "topology-device--selected" in response.text


def test_topology_canvas_supports_keyboard_selection() -> None:
    """Topology devices must be selectable with the keyboard."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert '"Enter"' in response.text
    assert '" "' in response.text
    assert 'setAttribute("tabindex", "0")' in response.text


def test_static_ui_contains_device_details_panel() -> None:
    """The dashboard must expose the premium device details panel."""
    client = make_client()

    response = client.get("/ui/")

    assert response.status_code == 200
    assert 'id="device-details"' in response.text
    assert 'id="device-details-icon"' in response.text
    assert 'id="device-details-title"' in response.text
    assert 'id="device-details-primary"' in response.text
    assert 'id="device-details-health"' in response.text
    assert 'id="device-details-supervision"' in response.text
    assert 'id="device-details-manufacturer"' in response.text
    assert 'id="device-links-list"' in response.text


def test_topology_canvas_supports_zoom() -> None:
    """The topology canvas must support controlled zoom."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "zoomIn(" in response.text
    assert "zoomOut(" in response.text
    assert "zoomAtPoint(" in response.text
    assert "MIN_ZOOM" in response.text
    assert "MAX_ZOOM" in response.text


def test_topology_canvas_supports_pan() -> None:
    """The topology canvas must support pointer panning."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "handlePointerDown(" in response.text
    assert "handlePointerMove(" in response.text
    assert "handlePointerUp(" in response.text
    assert "setPointerCapture(" in response.text


def test_topology_canvas_supports_wheel_navigation() -> None:
    """The topology canvas must support mouse wheel zoom."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "handleWheel(" in response.text
    assert '"wheel"' in response.text
    assert "passive: false" in response.text


def test_topology_canvas_can_reset_view() -> None:
    """The topology canvas must restore its initial viewport."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "resetView(" in response.text
    assert "initialViewBox" in response.text


def test_topology_canvas_can_fit_content_to_viewport() -> None:
    """The topology canvas must fit devices to the visible area."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "contentBounds(" in response.text
    assert "fitContentToViewport(" in response.text
    assert "getBoundingClientRect(" in response.text
    assert "requestAnimationFrame(" in response.text


def test_topology_canvas_styles_link_kinds() -> None:
    """Topology links must expose protocol-specific styles."""
    client = make_client()

    response = client.get("/ui/styles/topology.css")

    assert response.status_code == 200
    assert ".topology-link--ethernet" in response.text
    assert ".topology-link--wifi" in response.text
    assert ".topology-link--wireguard" in response.text
    assert ".topology-link--mqtt" in response.text
    assert ".topology-link--usb" in response.text
    assert ".topology-link--serial" in response.text


def test_topology_canvas_renders_only_directional_arrows() -> None:
    """Only genuinely directional links must display an arrow."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "createDirectionMarker(" in response.text
    assert "applyLinkDirection(" in response.text
    assert 'direction === "source_to_target"' in response.text
    assert '"marker-end"' in response.text
    assert '"marker-start"' not in response.text
    assert "Bidirectional links intentionally have no arrow." in response.text


def test_topology_canvas_applies_derived_link_health() -> None:
    """Rendered links must receive their derived endpoint health."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "this.linkHealth(link)" in response.text


def test_topology_canvas_renders_health_halos() -> None:
    """Device cards must expose a health halo layer."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "createDeviceHalo(" in response.text
    assert '"topology-device__halo"' in response.text


def test_topology_canvas_focuses_connected_path() -> None:
    """Selecting a device must highlight its direct topology path."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "sourceDeviceId" in response.text
    assert "targetDeviceId" in response.text
    assert '"topology-link--focused"' in response.text
    assert '"topology-link--dimmed"' in response.text
    assert '"topology-device--connected"' in response.text
    assert '"topology-device--dimmed"' in response.text


def test_topology_styles_animate_attention_states_accessibly() -> None:
    """Degraded and unhealthy halos must respect reduced motion."""
    client = make_client()

    response = client.get("/ui/styles/topology.css")

    assert response.status_code == 200
    assert "@keyframes topology-halo-pulse" in response.text
    assert "@keyframes topology-halo-alert" in response.text
    assert "prefers-reduced-motion: reduce" in response.text


def test_topology_canvas_staggers_animation_order() -> None:
    """Topology elements must expose a stable animation order."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert '"--topology-order"' in response.text
    assert "links.entries()" in response.text
    assert "devices.entries()" in response.text


def test_topology_styles_use_discreet_motion() -> None:
    """Topology motion must be contextual and unobtrusive."""
    client = make_client()

    response = client.get("/ui/styles/topology.css")

    assert response.status_code == 200
    assert "@keyframes topology-device-enter" in response.text
    assert "@keyframes topology-link-enter" in response.text
    assert "@keyframes topology-link-flow" in response.text
    assert "@keyframes topology-connector-pulse" in response.text
    assert ".topology-link--focused" in response.text


def test_topology_device_entry_animation_preserves_svg_position() -> None:
    """Device entry motion must not override the SVG positioning transform."""
    client = make_client()

    response = client.get("/ui/styles/topology.css")

    assert response.status_code == 200
    animation = response.text.split(
        "@keyframes topology-device-enter",
        maxsplit=1,
    )[1].split("@keyframes topology-link-enter", maxsplit=1)[0]
    assert "transform:" not in animation


def test_topology_canvas_supports_pinch_zoom() -> None:
    """Touch users must be able to zoom with two pointers."""
    client = make_client()

    response = client.get("/ui/topology_canvas.js")

    assert response.status_code == 200
    assert "activePointers" in response.text
    assert "currentPinchDistance(" in response.text
    assert "handlePinchZoom(" in response.text
    assert "Math.hypot(" in response.text


def test_topology_canvas_has_no_fixed_minimum_width() -> None:
    """The SVG must scale to narrow responsive viewports."""
    client = make_client()

    topology = client.get("/ui/styles/topology.css")
    responsive = client.get("/ui/styles/responsive.css")

    assert topology.status_code == 200
    assert responsive.status_code == 200
    assert "min-width: 64rem" not in topology.text
    assert "min-width: 48rem" not in responsive.text
    assert "min-width: 0" in topology.text


def test_topology_controls_keep_touch_sized_targets() -> None:
    """Map controls must remain comfortably usable by touch."""
    client = make_client()

    response = client.get("/ui/styles/topology.css")

    assert response.status_code == 200
    assert "min-width: 2.75rem" in response.text
    assert "height: 2.75rem" in response.text
