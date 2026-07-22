"""Tests for the infrastructure ingestion request model."""

import pytest
from pydantic import ValidationError

from ohanna_vision.web.infrastructure_request import (
    InfrastructureRequest,
)


def make_payload() -> dict[str, object]:
    """Build a valid infrastructure payload."""
    return {
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
    }


def test_infrastructure_request_accepts_valid_payload() -> None:
    request = InfrastructureRequest.model_validate(
        make_payload()
    )

    assert request.schema_version == 1
    assert request.infrastructure_id == "ohanna-house"
    assert request.nodes[0].node_id == "infra-01"
    assert (
        request.services[0].service_id
        == "dns-primary"
    )


def test_infrastructure_request_rejects_unknown_schema() -> None:
    payload = make_payload()
    payload["schema_version"] = 2

    with pytest.raises(ValidationError):
        InfrastructureRequest.model_validate(payload)


def test_infrastructure_request_rejects_duplicate_nodes() -> None:
    payload = make_payload()
    nodes = payload["nodes"]

    assert isinstance(nodes, list)

    nodes.append(dict(nodes[0]))

    with pytest.raises(
        ValidationError,
        match="node identifiers must be unique",
    ):
        InfrastructureRequest.model_validate(payload)


def test_infrastructure_request_rejects_duplicate_services() -> None:
    payload = make_payload()
    services = payload["services"]

    assert isinstance(services, list)

    services.append(dict(services[0]))

    with pytest.raises(
        ValidationError,
        match="service identifiers must be unique",
    ):
        InfrastructureRequest.model_validate(payload)


def test_infrastructure_request_rejects_unknown_service_node() -> None:
    payload = make_payload()
    services = payload["services"]

    assert isinstance(services, list)

    services[0]["node_id"] = "missing-node"

    with pytest.raises(
        ValidationError,
        match=(
            "services reference unknown node identifiers"
        ),
    ):
        InfrastructureRequest.model_validate(payload)


def test_infrastructure_request_rejects_extra_fields() -> None:
    payload = make_payload()
    payload["unexpected"] = True

    with pytest.raises(ValidationError):
        InfrastructureRequest.model_validate(payload)


def test_infrastructure_request_rejects_invalid_port() -> None:
    payload = make_payload()
    services = payload["services"]

    assert isinstance(services, list)

    services[0]["port"] = 70000

    with pytest.raises(ValidationError):
        InfrastructureRequest.model_validate(payload)

def make_topology_payload() -> dict[str, object]:
    """Build a complete topology payload."""
    payload = make_payload()
    payload["topology"] = {
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
                "label": "INFRA-01",
                "kind": "raspberry_pi",
                "node_id": "infra-01",
                "address": "192.168.1.10",
                "metadata": {},
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
                "metadata": {},
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
                "metadata": {},
            }
        ],
        "metadata": {
            "version": 1,
        },
    }
    return payload


def test_infrastructure_request_accepts_complete_topology() -> None:
    request = InfrastructureRequest.model_validate(
        make_topology_payload()
    )

    assert request.topology is not None
    assert request.topology.devices[1].node_id == "infra-01"
    assert request.topology.links[0].kind.value == "ethernet"
    assert (
        request.topology.layouts[0].positions["infra-device"].column
        == 1
    )


def test_infrastructure_request_rejects_duplicate_topology_devices() -> None:
    payload = make_topology_payload()
    topology = payload["topology"]

    assert isinstance(topology, dict)
    devices = topology["devices"]
    assert isinstance(devices, list)
    devices.append(dict(devices[0]))

    with pytest.raises(
        ValidationError,
        match="topology device identifiers must be unique",
    ):
        InfrastructureRequest.model_validate(payload)


def test_infrastructure_request_rejects_unknown_link_device() -> None:
    payload = make_topology_payload()
    topology = payload["topology"]

    assert isinstance(topology, dict)
    links = topology["links"]
    assert isinstance(links, list)
    links[0]["target_device_id"] = "missing"

    with pytest.raises(
        ValidationError,
        match="topology links reference unknown devices",
    ):
        InfrastructureRequest.model_validate(payload)


def test_infrastructure_request_rejects_unknown_topology_node() -> None:
    payload = make_topology_payload()
    topology = payload["topology"]

    assert isinstance(topology, dict)
    devices = topology["devices"]
    assert isinstance(devices, list)
    devices[1]["node_id"] = "missing-node"

    with pytest.raises(
        ValidationError,
        match="topology devices reference unknown node identifiers",
    ):
        InfrastructureRequest.model_validate(payload)


def test_infrastructure_request_rejects_duplicate_grid_cells() -> None:
    payload = make_topology_payload()
    topology = payload["topology"]

    assert isinstance(topology, dict)
    layouts = topology["layouts"]
    assert isinstance(layouts, list)
    positions = layouts[0]["positions"]
    assert isinstance(positions, dict)
    positions["infra-device"] = {
        "column": 0,
        "row": 1,
    }

    with pytest.raises(
        ValidationError,
        match="layout grid positions must be unique",
    ):
        InfrastructureRequest.model_validate(payload)
