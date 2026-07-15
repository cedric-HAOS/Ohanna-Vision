from datetime import UTC, datetime, timedelta

import pytest

from ohanna_vision.domain import (
    CapabilityState,
    Health,
    HealthStatus,
)


def test_capability_state_is_created() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    state = CapabilityState(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="zwave-01",
        health=Health(status=HealthStatus.HEALTHY),
        observed_at=observed_at,
        state_since=observed_at,
        latency_ms=3.86,
        message="DNS resolution succeeded.",
    )

    assert state.capability_id == "dns.resolve"
    assert state.health.status is HealthStatus.HEALTHY
    assert state.latency_ms == 3.86


def test_capability_state_calculates_state_duration() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    state = CapabilityState(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="zwave-01",
        health=Health(status=HealthStatus.HEALTHY),
        observed_at=observed_at,
        state_since=observed_at - timedelta(minutes=5),
    )

    assert state.duration_seconds == 300.0


def test_capability_state_rejects_naive_observation_date() -> None:
    with pytest.raises(
        ValueError,
        match="observed_at must be timezone-aware",
    ):
        CapabilityState(
            capability_id="dns.resolve",
            service_id="dns-primary",
            node_id="zwave-01",
            health=Health(status=HealthStatus.HEALTHY),
            observed_at=datetime(2026, 7, 10, 14, 0),
            state_since=datetime(2026, 7, 10, 14, 0, tzinfo=UTC),
        )


def test_capability_state_rejects_negative_latency() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    with pytest.raises(
        ValueError,
        match="latency_ms must not be negative",
    ):
        CapabilityState(
            capability_id="dns.resolve",
            service_id="dns-primary",
            node_id="zwave-01",
            health=Health(status=HealthStatus.HEALTHY),
            observed_at=observed_at,
            state_since=observed_at,
            latency_ms=-1.0,
        )
