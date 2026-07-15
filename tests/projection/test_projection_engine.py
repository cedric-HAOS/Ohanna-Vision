from datetime import UTC, datetime, timedelta

import pytest

from ohanna_vision.domain import HealthStatus, Observation
from ohanna_vision.projection import ProjectionEngine


def make_observation(
    *,
    node_id: str = "zwave-01",
    service_id: str = "dns-primary",
    capability_id: str = "dns.resolve",
    status: HealthStatus = HealthStatus.HEALTHY,
    observed_at: datetime,
) -> Observation:
    return Observation(
        capability_id=capability_id,
        service_id=service_id,
        node_id=node_id,
        status=status,
        observed_at=observed_at,
    )


def test_engine_projects_empty_infrastructure() -> None:
    infrastructure = ProjectionEngine().project([])

    assert infrastructure.nodes == ()


def test_engine_projects_complete_infrastructure() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    infrastructure = ProjectionEngine().project(
        [
            make_observation(observed_at=observed_at),
            make_observation(
                node_id="green-01",
                service_id="mqtt-primary",
                capability_id="mqtt.connect",
                observed_at=observed_at,
            ),
        ]
    )

    assert len(infrastructure.nodes) == 2
    assert len(infrastructure.services) == 2
    assert infrastructure.capability_count == 2


def test_engine_groups_capability_observations() -> None:
    first_date = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    second_date = first_date + timedelta(minutes=5)

    infrastructure = ProjectionEngine().project(
        [
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=first_date,
            ),
            make_observation(
                status=HealthStatus.DEGRADED,
                observed_at=second_date,
            ),
        ]
    )

    state = infrastructure.services[0].capabilities[0]

    assert state.health.status is HealthStatus.DEGRADED
    assert state.state_since == second_date


def test_engine_accepts_out_of_order_observations() -> None:
    first_date = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    second_date = first_date + timedelta(minutes=5)

    infrastructure = ProjectionEngine().project(
        [
            make_observation(
                status=HealthStatus.DEGRADED,
                observed_at=second_date,
            ),
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=first_date,
            ),
        ]
    )

    state = infrastructure.services[0].capabilities[0]

    assert state.health.status is HealthStatus.DEGRADED


def test_engine_projects_state_at_given_date() -> None:
    first_date = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    second_date = first_date + timedelta(minutes=5)

    observations = [
        make_observation(
            status=HealthStatus.HEALTHY,
            observed_at=first_date,
        ),
        make_observation(
            status=HealthStatus.UNAVAILABLE,
            observed_at=second_date,
        ),
    ]

    infrastructure = ProjectionEngine().project(
        observations,
        at=first_date,
    )

    state = infrastructure.services[0].capabilities[0]

    assert state.health.status is HealthStatus.HEALTHY
    assert state.observed_at == first_date


def test_engine_rejects_naive_projection_date() -> None:
    with pytest.raises(
        ValueError,
        match="at must be timezone-aware",
    ):
        ProjectionEngine().project(
            [],
            at=datetime(2026, 7, 10, 14, 0),
        )
