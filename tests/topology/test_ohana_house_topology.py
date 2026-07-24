"""Tests for the Ohana-House topology definition."""

from ohana_vision.topology import (
    TopologyDeviceKind,
    TopologyLayoutKind,
    TopologyLinkKind,
    build_ohana_house_topology,
)


def test_ohana_house_topology_has_expected_identity() -> None:
    """The topology must identify Ohana-House."""
    topology = build_ohana_house_topology()

    assert topology.topology_id == "ohana-house"
    assert topology.label == "Ohana-House"


def test_ohana_house_topology_contains_expected_devices() -> None:
    """The topology must contain current Ohana-House devices."""
    topology = build_ohana_house_topology()

    assert tuple(device.device_id for device in topology.devices) == (
        "internet",
        "freebox",
        "sw-01",
        "sw-02",
        "sw-03",
        "ap-01",
        "rpi-link",
        "ha-green",
        "rpi-zwave",
    )


def test_ohana_house_topology_contains_expected_links() -> None:
    """The topology must contain current physical links."""
    topology = build_ohana_house_topology()

    assert tuple(link.link_id for link in topology.links) == (
        "internet-freebox",
        "freebox-sw-01",
        "sw-01-sw-02",
        "sw-02-sw-03",
        "sw-01-ap-01",
        "ap-01-rpi-link",
        "sw-03-ha-green",
        "sw-03-rpi-zwave",
    )


def test_ohana_house_backbone_is_ten_gigabit() -> None:
    """The SW-01 to SW-02 backbone must expose 10 Gb."""
    topology = build_ohana_house_topology()

    link = topology.link("sw-01-sw-02")

    assert link is not None
    assert link.kind is TopologyLinkKind.ETHERNET
    assert link.bandwidth_mbps == 10_000


def test_ohana_house_rpi_link_uses_wifi() -> None:
    """RPI-LINK must be connected through AP-01 over Wi-Fi."""
    topology = build_ohana_house_topology()

    link = topology.link("ap-01-rpi-link")

    assert link is not None
    assert link.kind is TopologyLinkKind.WIFI
    assert link.source_device_id == "ap-01"
    assert link.target_device_id == "rpi-link"


def test_ohana_house_runtime_devices_reference_nodes() -> None:
    """Supervised devices must reference their runtime node identifiers."""
    topology = build_ohana_house_topology()

    assert topology.device("rpi-link").node_id == "rpi-link"  # type: ignore[union-attr]
    assert topology.device("ha-green").node_id == "ha-green"  # type: ignore[union-attr]
    assert topology.device("rpi-zwave").node_id == "rpi-zwave"  # type: ignore[union-attr]


def test_ohana_house_network_devices_have_expected_kinds() -> None:
    """Infrastructure devices must expose their visual kinds."""
    topology = build_ohana_house_topology()

    assert (
        topology.device("internet").kind  # type: ignore[union-attr]
        is TopologyDeviceKind.INTERNET
    )
    assert (
        topology.device("freebox").kind  # type: ignore[union-attr]
        is TopologyDeviceKind.ROUTER
    )
    assert (
        topology.device("sw-01").kind  # type: ignore[union-attr]
        is TopologyDeviceKind.SWITCH
    )
    assert (
        topology.device("ap-01").kind  # type: ignore[union-attr]
        is TopologyDeviceKind.ACCESS_POINT
    )


def test_ohana_house_topology_has_physical_layout() -> None:
    """The topology must expose its primary physical layout."""
    topology = build_ohana_house_topology()

    layout = topology.layout("ohana-house-physical")

    assert layout is not None
    assert layout.kind is TopologyLayoutKind.PHYSICAL
    assert layout.canvas_width == 1800
    assert layout.canvas_height == 820


def test_ohana_house_layout_positions_every_device() -> None:
    """Every current device must be positioned on the primary map."""
    topology = build_ohana_house_topology()
    layout = topology.layout("ohana-house-physical")

    assert layout is not None

    assert set(layout.positions) == {device.device_id for device in topology.devices}


def test_ohana_house_topology_is_coherent() -> None:
    """Every link and layout position must reference known devices."""
    topology = build_ohana_house_topology()

    device_ids = {device.device_id for device in topology.devices}

    for link in topology.links:
        assert link.source_device_id in device_ids
        assert link.target_device_id in device_ids

    for layout in topology.layouts:
        assert set(layout.positions).issubset(device_ids)


def test_ohana_house_layout_uses_a_regular_grid() -> None:
    """Device coordinates must follow constant grid spacing."""
    topology = build_ohana_house_topology()
    layout = topology.layout("ohana-house-physical")

    assert layout is not None

    assert layout.position_for("freebox").x - layout.position_for("internet").x == 300  # type: ignore[union-attr]
    assert layout.position_for("sw-01").x - layout.position_for("freebox").x == 300  # type: ignore[union-attr]
    assert layout.position_for("rpi-zwave").y - layout.position_for("ha-green").y == 260  # type: ignore[union-attr]


def test_ohana_house_layout_is_horizontal() -> None:
    """The network backbone must progress from left to right."""
    topology = build_ohana_house_topology()
    layout = topology.layout("ohana-house-physical")

    assert layout is not None

    backbone = ("internet", "freebox", "sw-01", "sw-02", "sw-03")
    x_coordinates = tuple(
        layout.position_for(device_id).x  # type: ignore[union-attr]
        for device_id in backbone
    )

    assert x_coordinates == tuple(sorted(x_coordinates))
