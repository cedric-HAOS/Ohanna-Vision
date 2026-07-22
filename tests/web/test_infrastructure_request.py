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