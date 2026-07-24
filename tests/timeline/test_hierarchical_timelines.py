from datetime import UTC, datetime, timedelta

import pytest

from ohana_vision.domain import HealthStatus
from ohana_vision.timeline import (
    CapabilityTimeline,
    InfrastructureTimeline,
    NodeTimeline,
    ServiceTimeline,
    StatePeriod,
)


def make_capability(
    *,
    capability_id: str = "dns.resolve",
    service_id: str = "dns-primary",
    node_id: str = "infra-01",
) -> CapabilityTimeline:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    return CapabilityTimeline(
        capability_id=capability_id,
        service_id=service_id,
        node_id=node_id,
        periods=(
            StatePeriod(
                status=HealthStatus.HEALTHY,
                started_at=started_at,
            ),
        ),
    )


def test_service_timeline_contains_capabilities() -> None:
    capability = make_capability()

    timeline = ServiceTimeline(
        service_id="dns-primary",
        node_id="infra-01",
        capabilities=(capability,),
        periods=capability.periods,
    )

    assert timeline.capability("dns.resolve") is capability
    assert timeline.current_status is HealthStatus.HEALTHY


def test_service_timeline_rejects_foreign_capability() -> None:
    capability = make_capability(service_id="mqtt-primary")

    with pytest.raises(
        ValueError,
        match="must belong to the service",
    ):
        ServiceTimeline(
            service_id="dns-primary",
            node_id="infra-01",
            capabilities=(capability,),
        )


def test_service_timeline_rejects_duplicate_capabilities() -> None:
    capability = make_capability()

    with pytest.raises(
        ValueError,
        match="capability identifiers must be unique",
    ):
        ServiceTimeline(
            service_id="dns-primary",
            node_id="infra-01",
            capabilities=(capability, capability),
        )


def test_node_timeline_contains_services() -> None:
    capability = make_capability()

    service = ServiceTimeline(
        service_id="dns-primary",
        node_id="infra-01",
        capabilities=(capability,),
        periods=capability.periods,
    )

    node = NodeTimeline(
        node_id="infra-01",
        services=(service,),
        periods=service.periods,
    )

    assert node.service("dns-primary") is service
    assert node.current_status is HealthStatus.HEALTHY


def test_node_timeline_rejects_foreign_service() -> None:
    service = ServiceTimeline(
        service_id="dns-primary",
        node_id="other-node",
    )

    with pytest.raises(
        ValueError,
        match="must belong to the node",
    ):
        NodeTimeline(
            node_id="infra-01",
            services=(service,),
        )


def test_infrastructure_timeline_contains_nodes() -> None:
    node = NodeTimeline(node_id="infra-01")

    infrastructure = InfrastructureTimeline(nodes=(node,))

    assert infrastructure.node("infra-01") is node


def test_infrastructure_timeline_rejects_duplicate_nodes() -> None:
    node = NodeTimeline(node_id="infra-01")

    with pytest.raises(
        ValueError,
        match="node identifiers must be unique",
    ):
        InfrastructureTimeline(nodes=(node, node))


def test_hierarchical_timeline_returns_status_at_instant() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    ended_at = started_at + timedelta(minutes=15)

    timeline = InfrastructureTimeline(
        periods=(
            StatePeriod(
                status=HealthStatus.DEGRADED,
                started_at=started_at,
                ended_at=ended_at,
            ),
        ),
    )

    assert (
        timeline.status_at(started_at + timedelta(minutes=5)) is HealthStatus.DEGRADED
    )
