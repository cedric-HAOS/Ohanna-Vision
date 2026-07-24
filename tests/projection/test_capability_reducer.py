from datetime import UTC, datetime, timedelta

import pytest

from ohana_vision.domain import HealthStatus, Observation
from ohana_vision.projection import (
    CapabilityReducer,
    EmptyCapabilityProjectionError,
    MixedCapabilityObservationsError,
)


def make_observation(
    *,
    status: HealthStatus,
    observed_at: datetime,
    capability_id: str = "dns.resolve",
) -> Observation:
    return Observation(
        capability_id=capability_id,
        service_id="dns-primary",
        node_id="zwave-01",
        status=status,
        observed_at=observed_at,
    )


def test_reducer_requires_observation() -> None:
    reducer = CapabilityReducer()

    with pytest.raises(EmptyCapabilityProjectionError):
        reducer.reduce([])


def test_reducer_uses_latest_observation() -> None:
    reducer = CapabilityReducer()
    first_date = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    second_date = first_date + timedelta(minutes=5)

    state = reducer.reduce(
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

    assert state.health.status is HealthStatus.DEGRADED
    assert state.observed_at == second_date


def test_reducer_preserves_continuous_state_since() -> None:
    reducer = CapabilityReducer()
    first_date = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    state = reducer.reduce(
        [
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=first_date,
            ),
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=first_date + timedelta(minutes=5),
            ),
        ]
    )

    assert state.state_since == first_date


def test_reducer_resets_state_since_after_transition() -> None:
    reducer = CapabilityReducer()
    first_date = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    transition_date = first_date + timedelta(minutes=5)

    state = reducer.reduce(
        [
            make_observation(
                status=HealthStatus.HEALTHY,
                observed_at=first_date,
            ),
            make_observation(
                status=HealthStatus.DEGRADED,
                observed_at=transition_date,
            ),
            make_observation(
                status=HealthStatus.DEGRADED,
                observed_at=transition_date + timedelta(minutes=5),
            ),
        ]
    )

    assert state.state_since == transition_date


def test_reducer_rejects_mixed_capabilities() -> None:
    reducer = CapabilityReducer()
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    with pytest.raises(MixedCapabilityObservationsError):
        reducer.reduce(
            [
                make_observation(
                    status=HealthStatus.HEALTHY,
                    observed_at=observed_at,
                ),
                make_observation(
                    status=HealthStatus.HEALTHY,
                    observed_at=observed_at,
                    capability_id="dns.latency",
                ),
            ]
        )
