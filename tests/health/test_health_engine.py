from datetime import UTC, datetime, timedelta

import pytest

from ohanna_vision.domain import (
    CapabilityState,
    Criticality,
    Health,
    HealthStatus,
    InfrastructureState,
    NodeState,
    ServiceState,
)
from ohanna_vision.health import (
    CapabilityHealthPolicy,
    DuplicateHealthPolicyError,
    HealthEngine,
)


def make_capability(
    *,
    node_id: str = "infra-01",
    service_id: str = "dns-primary",
    capability_id: str = "dns.resolve",
    status: HealthStatus = HealthStatus.HEALTHY,
    observed_at: datetime | None = None,
) -> CapabilityState:
    date = observed_at or datetime(
        2026,
        7,
        10,
        14,
        0,
        tzinfo=UTC,
    )

    return CapabilityState(
        capability_id=capability_id,
        service_id=service_id,
        node_id=node_id,
        health=Health(status=status),
        observed_at=date,
        state_since=date,
    )


def make_infrastructure(
    *capabilities: CapabilityState,
) -> InfrastructureState:
    services_by_node: dict[
        str,
        dict[str, list[CapabilityState]],
    ] = {}

    for capability in capabilities:
        node_services = services_by_node.setdefault(
            capability.node_id,
            {},
        )
        node_services.setdefault(
            capability.service_id,
            [],
        ).append(capability)

    nodes = []

    for node_id, services in services_by_node.items():
        service_states = tuple(
            ServiceState(
                service_id=service_id,
                node_id=node_id,
                capabilities=tuple(values),
            )
            for service_id, values in services.items()
        )

        nodes.append(
            NodeState(
                node_id=node_id,
                services=service_states,
            )
        )

    return InfrastructureState(nodes=tuple(nodes))


def test_engine_returns_unknown_for_empty_infrastructure() -> None:
    report = HealthEngine().evaluate(
        InfrastructureState(nodes=()),
        now=datetime(2026, 7, 10, 14, 0, tzinfo=UTC),
    )

    assert report.infrastructure.status is HealthStatus.UNKNOWN


def test_engine_preserves_healthy_capability() -> None:
    capability = make_capability()
    now = datetime(2026, 7, 10, 14, 1, tzinfo=UTC)

    report = HealthEngine().evaluate(
        make_infrastructure(capability),
        now=now,
    )

    assessment = report.capability(
        node_id="infra-01",
        service_id="dns-primary",
        capability_id="dns.resolve",
    )

    assert assessment is not None
    assert assessment.status is HealthStatus.HEALTHY
    assert report.infrastructure.status is HealthStatus.HEALTHY


def test_engine_marks_old_observation_as_stale() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    capability = make_capability(observed_at=observed_at)

    policy = CapabilityHealthPolicy(
        node_id="infra-01",
        service_id="dns-primary",
        capability_id="dns.resolve",
        stale_after=timedelta(minutes=5),
    )

    report = HealthEngine([policy]).evaluate(
        make_infrastructure(capability),
        now=observed_at + timedelta(minutes=6),
    )

    assessment = report.capability(
        node_id="infra-01",
        service_id="dns-primary",
        capability_id="dns.resolve",
    )

    assert assessment is not None
    assert assessment.status is HealthStatus.STALE


def test_recent_observation_does_not_become_stale() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    capability = make_capability(observed_at=observed_at)

    policy = CapabilityHealthPolicy(
        node_id="infra-01",
        service_id="dns-primary",
        capability_id="dns.resolve",
        stale_after=timedelta(minutes=5),
    )

    report = HealthEngine([policy]).evaluate(
        make_infrastructure(capability),
        now=observed_at + timedelta(minutes=5),
    )

    assessment = report.capability(
        node_id="infra-01",
        service_id="dns-primary",
        capability_id="dns.resolve",
    )

    assert assessment is not None
    assert assessment.status is HealthStatus.HEALTHY


def test_critical_unavailable_capability_makes_infrastructure_unavailable() -> None:
    capability = make_capability(
        status=HealthStatus.UNAVAILABLE,
    )

    policy = CapabilityHealthPolicy(
        node_id="infra-01",
        service_id="dns-primary",
        capability_id="dns.resolve",
        criticality=Criticality.CRITICAL,
    )

    report = HealthEngine([policy]).evaluate(
        make_infrastructure(capability),
        now=datetime(2026, 7, 10, 14, 1, tzinfo=UTC),
    )

    assert report.infrastructure.status is HealthStatus.UNAVAILABLE


def test_normal_unavailable_capability_only_degrades_infrastructure() -> None:
    capability = make_capability(
        status=HealthStatus.UNAVAILABLE,
    )

    report = HealthEngine().evaluate(
        make_infrastructure(capability),
        now=datetime(2026, 7, 10, 14, 1, tzinfo=UTC),
    )

    assert report.infrastructure.status is HealthStatus.DEGRADED


def test_stale_critical_capability_degrades_infrastructure() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    capability = make_capability(observed_at=observed_at)

    policy = CapabilityHealthPolicy(
        node_id="infra-01",
        service_id="dns-primary",
        capability_id="dns.resolve",
        criticality=Criticality.CRITICAL,
        stale_after=timedelta(minutes=5),
    )

    report = HealthEngine([policy]).evaluate(
        make_infrastructure(capability),
        now=observed_at + timedelta(minutes=6),
    )

    assert report.infrastructure.status is HealthStatus.DEGRADED


def test_engine_builds_service_and_node_assessments() -> None:
    capability = make_capability()

    report = HealthEngine().evaluate(
        make_infrastructure(capability),
        now=datetime(2026, 7, 10, 14, 1, tzinfo=UTC),
    )

    service = report.service(
        node_id="infra-01",
        service_id="dns-primary",
    )
    node = report.node("infra-01")

    assert service is not None
    assert service.status is HealthStatus.HEALTHY
    assert node is not None
    assert node.status is HealthStatus.HEALTHY


def test_engine_rejects_duplicate_policies() -> None:
    policy = CapabilityHealthPolicy(
        node_id="infra-01",
        service_id="dns-primary",
        capability_id="dns.resolve",
    )

    with pytest.raises(DuplicateHealthPolicyError):
        HealthEngine([policy, policy])


def test_engine_rejects_naive_evaluation_date() -> None:
    with pytest.raises(
        ValueError,
        match="now must be timezone-aware",
    ):
        HealthEngine().evaluate(
            InfrastructureState(nodes=()),
            now=datetime(2026, 7, 10, 14, 0),
        )
