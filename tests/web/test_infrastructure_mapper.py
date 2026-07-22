"""Tests for infrastructure-to-topology projection."""

from ohanna_vision.topology import (
    Topology,
    TopologyDevice,
    TopologyDeviceKind,
    TopologyLayout,
    TopologyLayoutKind,
    TopologyLink,
    TopologyLinkKind,
    TopologyPosition,
)
from ohanna_vision.web.infrastructure_mapper import (
    InfrastructureMapper,
)
from ohanna_vision.web.infrastructure_request import (
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
                "description": (
                    "Infrastructure server"
                ),
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
            "infrastructure_id": "ohanna-house",
            "name": "Ohanna House",
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
        topology_id="ohanna-house",
        label="Ohanna-House",
        devices=(
            TopologyDevice(
                device_id="infra-01",
                label="Old INFRA",
                kind=(
                    TopologyDeviceKind.RASPBERRY_PI
                ),
                node_id="infra-01",
                metadata={
                    "role": (
                        "infrastructure_server"
                    ),
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
    topology = InfrastructureMapper.to_topology(
        make_request()
    )

    assert topology.topology_id == "ohanna-house"
    assert topology.label == "Ohanna House"
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
    assert (
        device.kind
        is TopologyDeviceKind.RASPBERRY_PI
    )
    assert device.address == "192.168.1.10"
    assert (
        device.metadata["role"]
        == "infrastructure_server"
    )
    assert (
        device.metadata["manufacturer"]
        == "Raspberry Pi"
    )
    assert (
        device.metadata["source"]
        == "ohanna-agent"
    )

    assert topology.link_count == 1
    assert topology.layout("physical") is not None


def test_mapper_attaches_node_services() -> None:
    topology = InfrastructureMapper.to_topology(
        make_request()
    )

    device = topology.device("infra-01")

    assert device is not None

    assert device.metadata["services"] == (
        {
            "service_id": "dns-primary",
            "name": "Primary DNS",
            "type": "dns",
            "port": 53,
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
    assert (
        layout.position_for("ha-green")
        is not None
    )


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
    topology = InfrastructureMapper.to_topology(
        make_request()
    )

    assert (
        topology.metadata["source"]
        == "ohanna-agent"
    )
    assert topology.metadata["schema_version"] == 1
    assert (
        topology.metadata["environment"]
        == "production"
    )
    assert (
        topology.metadata[
            "configuration_version"
        ]
        == "1.0"
    )
    assert topology.metadata["tags"] == (
        "production",
        "home",
    )
    assert topology.metadata["service_count"] == 1