"""Tests for topology API mapping."""

from ohana_vision.topology import (
    Topology,
    TopologyDevice,
    TopologyDeviceKind,
    TopologyLayout,
    TopologyLayoutKind,
    TopologyLink,
    TopologyLinkDirection,
    TopologyLinkKind,
    TopologyPosition,
)
from ohana_vision.web.api.topology_mapper import (
    topology_to_response,
)


def make_topology() -> Topology:
    """Create a complete topology for mapper tests."""
    return Topology(
        topology_id="ohana-house",
        label="Ohana-House",
        devices=(
            TopologyDevice(
                device_id="sw-01",
                label="SW-01",
                kind=TopologyDeviceKind.SWITCH,
                node_id="infra-01",
                address="192.168.1.2",
                metadata={
                    "ports": {
                        "total": 8,
                    },
                },
            ),
            TopologyDevice(
                device_id="ha-green",
                label="HA-Green",
                kind=TopologyDeviceKind.HOME_ASSISTANT,
                node_id="ha-green",
                address="192.168.1.20",
            ),
        ),
        links=(
            TopologyLink(
                link_id="sw-01-ha-green",
                source_device_id="sw-01",
                target_device_id="ha-green",
                kind=TopologyLinkKind.ETHERNET,
                direction=TopologyLinkDirection.BIDIRECTIONAL,
                bandwidth_mbps=1000,
                metadata={
                    "ports": [
                        "1",
                        "eth0",
                    ],
                },
            ),
        ),
        layouts=(
            TopologyLayout(
                layout_id="physical-main",
                label="Carte physique",
                kind=TopologyLayoutKind.PHYSICAL,
                canvas_width=1600,
                canvas_height=900,
                positions={
                    "sw-01": TopologyPosition(
                        x=800,
                        y=300,
                        pinned=True,
                    ),
                    "ha-green": TopologyPosition(
                        x=800,
                        y=500,
                    ),
                },
            ),
        ),
        metadata={
            "version": 1,
        },
    )


def test_topology_mapper_maps_identity() -> None:
    """The mapper must preserve topology identity."""
    response = topology_to_response(make_topology())

    assert response.topology_id == "ohana-house"
    assert response.label == "Ohana-House"


def test_topology_mapper_maps_devices() -> None:
    """The mapper must expose topology devices."""
    response = topology_to_response(make_topology())

    assert len(response.devices) == 2

    device = response.devices[0]

    assert device.device_id == "sw-01"
    assert device.kind == "switch"
    assert device.node_id == "infra-01"
    assert device.address == "192.168.1.2"
    assert device.metadata == {
        "ports": {
            "total": 8,
        },
    }


def test_topology_mapper_maps_links() -> None:
    """The mapper must expose topology links."""
    response = topology_to_response(make_topology())

    assert len(response.links) == 1

    link = response.links[0]

    assert link.link_id == "sw-01-ha-green"
    assert link.source_device_id == "sw-01"
    assert link.target_device_id == "ha-green"
    assert link.kind == "ethernet"
    assert link.direction == "bidirectional"
    assert link.bandwidth_mbps == 1000
    assert link.metadata == {
        "ports": [
            "1",
            "eth0",
        ],
    }


def test_topology_mapper_maps_layouts() -> None:
    """The mapper must expose topology layouts and positions."""
    response = topology_to_response(make_topology())

    assert len(response.layouts) == 1

    layout = response.layouts[0]

    assert layout.layout_id == "physical-main"
    assert layout.kind == "physical"
    assert layout.canvas_width == 1600
    assert layout.canvas_height == 900

    position = layout.positions["sw-01"]

    assert position.x == 800
    assert position.y == 300
    assert position.layer == 0
    assert position.pinned is True


def test_topology_mapper_creates_mutable_api_metadata() -> None:
    """API metadata must not retain immutable domain wrappers."""
    response = topology_to_response(make_topology())

    response.metadata["version"] = 2
    response.devices[0].metadata["ports"]["total"] = 16

    assert response.metadata["version"] == 2
    assert response.devices[0].metadata == {
        "ports": {
            "total": 16,
        },
    }
