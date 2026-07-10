from datetime import UTC, datetime, timedelta

import pytest

from ohanna_vision.domain import HealthStatus, Observation
from ohanna_vision.timeline import (
    ConflictingTimelineObservationsError,
    MixedTimelineObservationsError,
    TimelineEngine,
)


def make_observation(
    *,
    status: HealthStatus,
    observed_at: datetime,
    capability_id: str = "dns.resolve",
    service_id: str = "dns-primary",
    node_id: str = "infra-01",
) -> Observation:
    return Observation(
        capability_id=capability_id,
        service_id=service_id,
        node_id=node_id,
        status=status,
        observed_at=observed_at,
    )


def test_engine_requires_observation() -> None:
    with pytest.raises(
        ValueError,
        match="At least one observation is required",
    ):
        TimelineEngine().build([])


def test_engine_builds_open_period_from_single_observation() -> None:
    observed_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    timeline = TimelineEngine().build(
        [
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=observed_at,
            )
        ]
    )

    assert timeline.capability_id == "dns.resolve"
    assert len(timeline.periods) == 1
    assert timeline.current_status is HealthStatus.HEALTHY
    assert timeline.current_period is not None
    assert timeline.current_period.started_at == observed_at


def test_engine_merges_consecutive_identical_statuses() -> None:
    first_date = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    timeline = TimelineEngine().build(
        [
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=first_date,
            ),
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=first_date + timedelta(minutes=5),
            ),
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=first_date + timedelta(minutes=10),
            ),
        ]
    )

    assert len(timeline.periods) == 1
    assert timeline.periods[0].started_at == first_date
    assert timeline.periods[0].is_open is True


def test_engine_creates_period_for_each_status_transition() -> None:
    first_date = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    degraded_at = first_date + timedelta(minutes=10)
    recovered_at = degraded_at + timedelta(minutes=10)

    timeline = TimelineEngine().build(
        [
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=first_date,
            ),
            make_observation(
                status=HealthStatus.DEGRADED,
                observed_at=degraded_at,
            ),
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=recovered_at,
            ),
        ]
    )

    assert len(timeline.periods) == 3

    assert timeline.periods[0].status is HealthStatus.HEALTHY
    assert timeline.periods[0].started_at == first_date
    assert timeline.periods[0].ended_at == degraded_at

    assert timeline.periods[1].status is HealthStatus.DEGRADED
    assert timeline.periods[1].started_at == degraded_at
    assert timeline.periods[1].ended_at == recovered_at

    assert timeline.periods[2].status is HealthStatus.HEALTHY
    assert timeline.periods[2].started_at == recovered_at
    assert timeline.periods[2].is_open is True


def test_engine_accepts_out_of_order_observations() -> None:
    first_date = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    second_date = first_date + timedelta(minutes=10)

    timeline = TimelineEngine().build(
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

    assert timeline.periods[0].status is HealthStatus.HEALTHY
    assert timeline.periods[0].started_at == first_date
    assert timeline.periods[0].ended_at == second_date
    assert timeline.current_status is HealthStatus.DEGRADED


def test_engine_closes_last_period_at_until() -> None:
    observed_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    until = observed_at + timedelta(hours=1)

    timeline = TimelineEngine().build(
        [
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=observed_at,
            )
        ],
        until=until,
    )

    assert timeline.current_period is None
    assert timeline.ended_at == until
    assert timeline.periods[0].duration == timedelta(hours=1)


def test_engine_ignores_observations_after_until() -> None:
    first_date = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    until = first_date + timedelta(minutes=10)
    later_date = first_date + timedelta(minutes=20)

    timeline = TimelineEngine().build(
        [
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=first_date,
            ),
            make_observation(
                status=HealthStatus.UNAVAILABLE,
                observed_at=later_date,
            ),
        ],
        until=until,
    )

    assert len(timeline.periods) == 1
    assert timeline.periods[0].status is HealthStatus.HEALTHY
    assert timeline.periods[0].ended_at == until


def test_engine_rejects_when_until_precedes_all_observations() -> None:
    observed_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    until = observed_at - timedelta(minutes=1)

    with pytest.raises(
        ValueError,
        match="At least one observation is required",
    ):
        TimelineEngine().build(
            [
                make_observation(
                    status=HealthStatus.HEALTHY,
                    observed_at=observed_at,
                )
            ],
            until=until,
        )


def test_engine_rejects_mixed_capabilities() -> None:
    observed_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    with pytest.raises(MixedTimelineObservationsError):
        TimelineEngine().build(
            [
                make_observation(
                    status=HealthStatus.HEALTHY,
                    observed_at=observed_at,
                ),
                make_observation(
                    status=HealthStatus.HEALTHY,
                    observed_at=observed_at + timedelta(minutes=5),
                    capability_id="dns.latency",
                ),
            ]
        )


def test_engine_accepts_same_status_at_same_instant() -> None:
    observed_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    timeline = TimelineEngine().build(
        [
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=observed_at,
            ),
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=observed_at,
            ),
        ]
    )

    assert len(timeline.periods) == 1
    assert timeline.current_status is HealthStatus.HEALTHY


def test_engine_rejects_conflicting_statuses_at_same_instant() -> None:
    observed_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    with pytest.raises(ConflictingTimelineObservationsError):
        TimelineEngine().build(
            [
                make_observation(
                    status=HealthStatus.HEALTHY,
                    observed_at=observed_at,
                ),
                make_observation(
                    status=HealthStatus.UNAVAILABLE,
                    observed_at=observed_at,
                ),
            ]
        )


def test_engine_rejects_naive_until() -> None:
    observed_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    with pytest.raises(
        ValueError,
        match="until must be timezone-aware",
    ):
        TimelineEngine().build(
            [
                make_observation(
                    status=HealthStatus.HEALTHY,
                    observed_at=observed_at,
                )
            ],
            until=datetime(2026, 7, 10, 9, 0),
        )

def test_engine_builds_complete_timeline_hierarchy() -> None:
    observed_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    infrastructure = TimelineEngine().build_infrastructure(
        [
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=observed_at,
            ),
            make_observation(
                node_id="green-01",
                service_id="mqtt-primary",
                capability_id="mqtt.connect",
                status=HealthStatus.HEALTHY,
                observed_at=observed_at,
            ),
        ]
    )

    assert len(infrastructure.nodes) == 2
    assert infrastructure.node("infra-01") is not None
    assert infrastructure.node("green-01") is not None
    assert infrastructure.current_status is HealthStatus.HEALTHY


def test_service_timeline_uses_most_severe_capability_status() -> None:
    first_date = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    degraded_at = first_date + timedelta(minutes=10)

    infrastructure = TimelineEngine().build_infrastructure(
        [
            make_observation(
                capability_id="dns.resolve",
                status=HealthStatus.HEALTHY,
                observed_at=first_date,
            ),
            make_observation(
                capability_id="dns.resolve",
                status=HealthStatus.DEGRADED,
                observed_at=degraded_at,
            ),
            make_observation(
                capability_id="dns.latency",
                status=HealthStatus.HEALTHY,
                observed_at=first_date,
            ),
        ]
    )

    node = infrastructure.node("infra-01")
    assert node is not None

    service = node.service("dns-primary")
    assert service is not None
    assert service.current_status is HealthStatus.DEGRADED


def test_node_timeline_uses_most_severe_service_status() -> None:
    observed_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    infrastructure = TimelineEngine().build_infrastructure(
        [
            make_observation(
                service_id="dns-primary",
                capability_id="dns.resolve",
                status=HealthStatus.HEALTHY,
                observed_at=observed_at,
            ),
            make_observation(
                service_id="ntp-primary",
                capability_id="ntp.sync",
                status=HealthStatus.UNAVAILABLE,
                observed_at=observed_at,
            ),
        ]
    )

    node = infrastructure.node("infra-01")

    assert node is not None
    assert node.current_status is HealthStatus.UNAVAILABLE


def test_infrastructure_uses_most_severe_node_status() -> None:
    observed_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    infrastructure = TimelineEngine().build_infrastructure(
        [
            make_observation(
                node_id="infra-01",
                status=HealthStatus.HEALTHY,
                observed_at=observed_at,
            ),
            make_observation(
                node_id="green-01",
                service_id="mqtt-primary",
                capability_id="mqtt.connect",
                status=HealthStatus.DEGRADED,
                observed_at=observed_at,
            ),
        ]
    )

    assert infrastructure.current_status is HealthStatus.DEGRADED


def test_hierarchical_timeline_merges_identical_parent_periods() -> None:
    first_date = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    second_date = first_date + timedelta(minutes=10)
    third_date = second_date + timedelta(minutes=10)

    infrastructure = TimelineEngine().build_infrastructure(
        [
            make_observation(
                capability_id="dns.resolve",
                status=HealthStatus.DEGRADED,
                observed_at=first_date,
            ),
            make_observation(
                capability_id="dns.resolve",
                status=HealthStatus.HEALTHY,
                observed_at=second_date,
            ),
            make_observation(
                capability_id="dns.latency",
                status=HealthStatus.UNAVAILABLE,
                observed_at=first_date,
            ),
            make_observation(
                capability_id="dns.latency",
                status=HealthStatus.DEGRADED,
                observed_at=third_date,
            ),
        ]
    )

    node = infrastructure.node("infra-01")
    assert node is not None

    service = node.service("dns-primary")
    assert service is not None

    assert len(service.periods) == 2
    assert service.periods[0].status is HealthStatus.UNAVAILABLE
    assert service.periods[1].status is HealthStatus.DEGRADED


def test_engine_builds_empty_infrastructure_timeline() -> None:
    infrastructure = TimelineEngine().build_infrastructure([])

    assert infrastructure.nodes == ()
    assert infrastructure.periods == ()
    assert infrastructure.current_status is None