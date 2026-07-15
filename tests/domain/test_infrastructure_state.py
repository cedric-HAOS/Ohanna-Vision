from datetime import UTC, datetime

import pytest

from ohanna_vision.domain import (
    CapabilityState,
    Health,
    HealthStatus,
    InfrastructureState,
    NodeState,
    ServiceState,
)


def make_node(
    node_id: str,
    service_id: str,
    status: HealthStatus,
) -> NodeState:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    capability = CapabilityState(
        capability_id=f"{service_id}.availability",
        service_id=service_id,
        node_id=node_id,
        health=Health(status=status),
        observed_at=observed_at,
        state_since=observed_at,
    )

    service = ServiceState(
        service_id=service_id,
        node_id=node_id,
        capabilities=(capability,),
    )

    return NodeState(
        node_id=node_id,
        services=(service,),
    )


def test_infrastructure_state_aggregates_node_health() -> None:
    infrastructure = InfrastructureState(
        nodes=(
            make_node(
                "zwave-01",
                "dns-primary",
                HealthStatus.HEALTHY,
            ),
            make_node(
                "green-01",
                "mqtt-primary",
                HealthStatus.DEGRADED,
            ),
        ),
    )

    assert infrastructure.health.status is HealthStatus.DEGRADED


def test_infrastructure_state_exposes_all_services() -> None:
    infrastructure = InfrastructureState(
        nodes=(
            make_node(
                "zwave-01",
                "dns-primary",
                HealthStatus.HEALTHY,
            ),
            make_node(
                "green-01",
                "mqtt-primary",
                HealthStatus.HEALTHY,
            ),
        ),
    )

    assert len(infrastructure.services) == 2
    assert infrastructure.capability_count == 2


def test_infrastructure_state_finds_node_and_service() -> None:
    node = make_node(
        "zwave-01",
        "dns-primary",
        HealthStatus.HEALTHY,
    )

    infrastructure = InfrastructureState(nodes=(node,))

    assert infrastructure.node("zwave-01") is node
    assert infrastructure.service("dns-primary") is node.services[0]


def test_infrastructure_state_rejects_duplicate_node_ids() -> None:
    first_node = make_node(
        "zwave-01",
        "dns-primary",
        HealthStatus.HEALTHY,
    )
    second_node = make_node(
        "zwave-01",
        "ntp-primary",
        HealthStatus.HEALTHY,
    )

    with pytest.raises(
        ValueError,
        match="node identifiers must be unique",
    ):
        InfrastructureState(
            nodes=(first_node, second_node),
        )
