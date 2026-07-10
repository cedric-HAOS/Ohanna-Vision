from datetime import UTC, datetime

import pytest

from ohanna_vision.domain import (
    CapabilityState,
    Health,
    HealthStatus,
    NodeState,
    ServiceState,
)


def make_service(
    service_id: str,
    status: HealthStatus,
) -> ServiceState:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    capability = CapabilityState(
        capability_id=f"{service_id}.availability",
        service_id=service_id,
        node_id="zwave-01",
        health=Health(status=status),
        observed_at=observed_at,
        state_since=observed_at,
    )

    return ServiceState(
        service_id=service_id,
        node_id="zwave-01",
        capabilities=(capability,),
    )


def test_node_state_aggregates_service_health() -> None:
    node = NodeState(
        node_id="zwave-01",
        services=(
            make_service("dns-primary", HealthStatus.HEALTHY),
            make_service("mqtt-primary", HealthStatus.UNAVAILABLE),
        ),
    )

    assert node.health.status is HealthStatus.UNAVAILABLE


def test_node_state_finds_service() -> None:
    service = make_service(
        "dns-primary",
        HealthStatus.HEALTHY,
    )

    node = NodeState(
        node_id="zwave-01",
        services=(service,),
    )

    assert node.service("dns-primary") is service
    assert node.service("unknown") is None


def test_node_state_rejects_foreign_service() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    capability = CapabilityState(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="linky-01",
        health=Health(status=HealthStatus.HEALTHY),
        observed_at=observed_at,
        state_since=observed_at,
    )

    service = ServiceState(
        service_id="dns-primary",
        node_id="linky-01",
        capabilities=(capability,),
    )

    with pytest.raises(
        ValueError,
        match="Every service must belong to the node",
    ):
        NodeState(
            node_id="zwave-01",
            services=(service,),
        )