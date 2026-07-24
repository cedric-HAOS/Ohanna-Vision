"""Tests for infrastructure-to-topology projection."""

from ohana_vision.topology import (
    Topology,
    TopologyDevice,
    TopologyDeviceKind,
    TopologyLayout,
    TopologyLayoutKind,
    TopologyLink,
    TopologyLinkKind,
    TopologyPosition,
)
from ohana_vision.web.infrastructure_mapper import (
    InfrastructureMapper,
)
from ohana_vision.web.infrastructure_request import (
    InfrastructureRequest,
)


def make_request(
    *,
    nodes: list[dict[str, object]] | None = None,
    services: list[dict[str, object]] | None = None,
) -> InfrastructureRequest:
    """Build a valid infrastructure request."""
    resolved_nodes = (
        nodes
        if nodes is not None
        else [
            {
                "node_id": "infra-01",
                "name": "INFRA-01",
                "description": ("Infrastructure server"),
                "endpoint": {
                    "type": "ip",
                    "address": "192.168.1.10",
                },
            }
        ]
    )

    resolved_services = (
        services
        if services is not None
        else [
            {
                "service_id": "dns-primary",
                "name": "Primary DNS",
                "type": "dns",
                "node_id": "infra-01",
                "port": 53,
            }
        ]
    )

    return InfrastructureRequest.model_validate(
        {
            "schema_version": 1,
            "infrastructure_id": "ohana-house",
            "name": "Ohana House",
            "environment": "production",
            "metadata": {
                "version": "1.0",
                "tags": [
                    "production",
                    "home",
                ],
            },
            "nodes": resolved_nodes,
            "services": resolved_services,
        }
    )


def make_base_topology() -> Topology:
    """Build a physical presentation topology."""
    return Topology(
        topology_id="ohana-house",
        label="Ohana-House",
        devices=(
            TopologyDevice(
                device_id="infra-01",
                label="Old INFRA",
                kind=(TopologyDeviceKind.RASPBERRY_PI),
                node_id="infra-01",
                metadata={
                    "role": ("infrastructure_server"),
                    "manufacturer": "Raspberry Pi",
                },
            ),
            TopologyDevice(
                device_id="switch-01",
                label="Switch",
                kind=TopologyDeviceKind.SWITCH,
            ),
        ),
        links=(
            TopologyLink(
                link_id="switch-infra",
                source_device_id="switch-01",
                target_device_id="infra-01",
                kind=TopologyLinkKind.ETHERNET,
            ),
        ),
        layouts=(
            TopologyLayout(
                layout_id="physical",
                label="Physical",
                kind=TopologyLayoutKind.PHYSICAL,
                positions={
                    "switch-01": TopologyPosition(
                        x=150,
                        y=150,
                    ),
                    "infra-01": TopologyPosition(
                        x=450,
                        y=150,
                    ),
                },
            ),
        ),
        metadata={
            "profile": "house",
        },
    )


def test_mapper_builds_topology_without_base() -> None:
    topology = InfrastructureMapper.to_topology(make_request())

    assert topology.topology_id == "ohana-house"
    assert topology.label == "Ohana House"
    assert topology.device_count == 1
    assert topology.link_count == 0
    assert topology.layout_count == 1

    device = topology.devices[0]

    assert device.device_id == "infra-01"
    assert device.label == "INFRA-01"
    assert device.kind is TopologyDeviceKind.SERVER
    assert device.node_id == "infra-01"
    assert device.address == "192.168.1.10"

    layout = topology.layouts[0]

    assert layout.kind is TopologyLayoutKind.LOGICAL
    assert layout.contains_device("infra-01")


def test_mapper_enriches_existing_device() -> None:
    topology = InfrastructureMapper.to_topology(
        make_request(),
        base_topology=make_base_topology(),
    )

    device = topology.device("infra-01")

    assert device is not None
    assert device.label == "INFRA-01"
    assert device.kind is TopologyDeviceKind.RASPBERRY_PI
    assert device.address == "192.168.1.10"
    assert device.metadata["role"] == "infrastructure_server"
    assert device.metadata["manufacturer"] == "Raspberry Pi"
    assert device.metadata["source"] == "ohana-agent"

    assert topology.link_count == 1
    assert topology.layout("physical") is not None


def test_mapper_attaches_node_services() -> None:
    topology = InfrastructureMapper.to_topology(make_request())

    device = topology.device("infra-01")

    assert device is not None

    assert device.metadata["services"] == (
        {
            "service_id": "dns-primary",
            "name": "Primary DNS",
            "type": "dns",
            "port": 53,
            "implementation": None,
            "enabled": True,
            "critical": False,
            "metadata": {},
        },
    )


def test_mapper_adds_unknown_node_to_layout() -> None:
    request = make_request(
        nodes=[
            {
                "node_id": "ha-green",
                "name": "HA-Green",
                "description": "Home Assistant",
                "endpoint": {
                    "type": "ip",
                    "address": "192.168.1.20",
                },
            }
        ],
        services=[],
    )

    topology = InfrastructureMapper.to_topology(
        request,
        base_topology=make_base_topology(),
    )

    assert topology.contains_device("ha-green")

    layout = topology.layout("physical")

    assert layout is not None
    assert layout.contains_device("ha-green")
    assert layout.position_for("ha-green") is not None


def test_mapper_rebuilds_from_stable_base() -> None:
    base = make_base_topology()

    first = InfrastructureMapper.to_topology(
        make_request(
            nodes=[
                {
                    "node_id": "first",
                    "name": "First",
                    "description": "",
                    "endpoint": {
                        "type": "ip",
                        "address": "192.168.1.30",
                    },
                }
            ],
            services=[],
        ),
        base_topology=base,
    )

    second = InfrastructureMapper.to_topology(
        make_request(
            nodes=[
                {
                    "node_id": "second",
                    "name": "Second",
                    "description": "",
                    "endpoint": {
                        "type": "ip",
                        "address": "192.168.1.31",
                    },
                }
            ],
            services=[],
        ),
        base_topology=base,
    )

    assert first.contains_device("first")
    assert not first.contains_device("second")

    assert second.contains_device("second")
    assert not second.contains_device("first")


def test_mapper_exposes_snapshot_metadata() -> None:
    topology = InfrastructureMapper.to_topology(make_request())

    assert topology.metadata["source"] == "ohana-agent"
    assert topology.metadata["schema_version"] == 1
    assert topology.metadata["environment"] == "production"
    assert topology.metadata["configuration_version"] == "1.0"
    assert topology.metadata["tags"] == (
        "production",
        "home",
    )
    assert topology.metadata["service_count"] == 1


def make_request_with_topology() -> InfrastructureRequest:
    """Build a snapshot containing a complete logical-grid topology."""
    return InfrastructureRequest.model_validate(
        {
            "schema_version": 1,
            "infrastructure_id": "ohana-house",
            "name": "Ohana House",
            "environment": "production",
            "metadata": {
                "version": "1.0",
                "tags": ["production", "home"],
            },
            "nodes": [
                {
                    "node_id": "infra-01",
                    "name": "INFRA-01",
                    "description": "Infrastructure server",
                    "endpoint": {
                        "type": "ip",
                        "address": "192.168.1.10",
                    },
                }
            ],
            "services": [
                {
                    "service_id": "dns-primary",
                    "name": "Primary DNS",
                    "type": "dns",
                    "node_id": "infra-01",
                    "port": 53,
                }
            ],
            "topology": {
                "devices": [
                    {
                        "device_id": "internet",
                        "label": "Internet",
                        "kind": "internet",
                        "node_id": None,
                        "address": None,
                        "metadata": {
                            "role": "external_network",
                        },
                    },
                    {
                        "device_id": "infra-device",
                        "label": "Infrastructure appliance",
                        "kind": "raspberry_pi",
                        "node_id": "infra-01",
                        "address": None,
                        "metadata": {
                            "role": "infrastructure_server",
                        },
                    },
                ],
                "links": [
                    {
                        "link_id": "internet-infra",
                        "source_device_id": "internet",
                        "target_device_id": "infra-device",
                        "kind": "ethernet",
                        "direction": "bidirectional",
                        "label": "WAN",
                        "bandwidth_mbps": 1000,
                        "metadata": {
                            "role": "uplink",
                        },
                    }
                ],
                "layouts": [
                    {
                        "layout_id": "physical",
                        "label": "Physical",
                        "kind": "physical",
                        "positions": {
                            "internet": {
                                "column": 0,
                                "row": 1,
                            },
                            "infra-device": {
                                "column": 1,
                                "row": 1,
                            },
                        },
                        "metadata": {
                            "description": "Horizontal layout",
                        },
                    }
                ],
                "metadata": {
                    "version": 1,
                },
            },
        }
    )


def test_mapper_uses_complete_declared_topology() -> None:
    topology = InfrastructureMapper.to_topology(
        make_request_with_topology(),
        base_topology=make_base_topology(),
    )

    assert topology.device_count == 2
    assert topology.link_count == 1
    assert topology.layout_count == 1
    assert not topology.contains_device("switch-01")
    assert topology.contains_device("internet")
    assert topology.contains_device("infra-device")


def test_mapper_enriches_declared_device_from_node() -> None:
    topology = InfrastructureMapper.to_topology(make_request_with_topology())
    device = topology.device("infra-device")

    assert device is not None
    assert device.label == "Infrastructure appliance"
    assert device.kind is TopologyDeviceKind.RASPBERRY_PI
    assert device.node_id == "infra-01"
    assert device.address == "192.168.1.10"
    assert device.metadata["role"] == "infrastructure_server"
    assert device.metadata["source"] == "ohana-agent"
    assert device.metadata["services"] == (
        {
            "service_id": "dns-primary",
            "name": "Primary DNS",
            "type": "dns",
            "port": 53,
            "implementation": None,
            "enabled": True,
            "critical": False,
            "metadata": {},
        },
    )


def test_mapper_maps_declared_links() -> None:
    topology = InfrastructureMapper.to_topology(make_request_with_topology())
    link = topology.links[0]

    assert link.link_id == "internet-infra"
    assert link.source_device_id == "internet"
    assert link.target_device_id == "infra-device"
    assert link.kind is TopologyLinkKind.ETHERNET
    assert link.direction.value == "bidirectional"
    assert link.bandwidth_mbps == 1000
    assert link.metadata["role"] == "uplink"


def test_mapper_projects_grid_to_horizontal_canvas() -> None:
    topology = InfrastructureMapper.to_topology(make_request_with_topology())
    layout = topology.layouts[0]
    internet = layout.position_for("internet")
    infrastructure = layout.position_for("infra-device")

    assert internet == TopologyPosition(
        x=150,
        y=410,
        layer=0,
        pinned=True,
    )
    assert infrastructure == TopologyPosition(
        x=450,
        y=410,
        layer=1,
        pinned=True,
    )
    assert layout.canvas_width == 600
    assert layout.canvas_height == 560


def test_mapper_preserves_declared_topology_metadata() -> None:
    topology = InfrastructureMapper.to_topology(make_request_with_topology())

    assert topology.metadata["version"] == 1
    assert topology.metadata["source"] == "ohana-agent"
    assert topology.metadata["configuration_version"] == "1.0"
