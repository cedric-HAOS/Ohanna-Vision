from datetime import UTC, datetime

import pytest

from ohana_vision.domain import HealthStatus, Observation


def test_observation_is_created() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    observation = Observation(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="zwave-01",
        status=HealthStatus.HEALTHY,
        observed_at=observed_at,
        latency_ms=3.86,
        message="DNS resolution succeeded.",
        metadata={"hostname": "example.com"},
    )

    assert observation.capability_id == "dns.resolve"
    assert observation.status is HealthStatus.HEALTHY
    assert observation.metadata["hostname"] == "example.com"


def test_observation_generates_identifier() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    first = Observation(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="zwave-01",
        status=HealthStatus.HEALTHY,
        observed_at=observed_at,
    )
    second = Observation(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="zwave-01",
        status=HealthStatus.HEALTHY,
        observed_at=observed_at,
    )

    assert first.observation_id != second.observation_id


def test_observation_rejects_naive_date() -> None:
    with pytest.raises(
        ValueError,
        match="observed_at must be timezone-aware",
    ):
        Observation(
            capability_id="dns.resolve",
            service_id="dns-primary",
            node_id="zwave-01",
            status=HealthStatus.HEALTHY,
            observed_at=datetime(2026, 7, 10, 14, 0),
        )


def test_observation_rejects_negative_latency() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    with pytest.raises(
        ValueError,
        match="latency_ms must not be negative",
    ):
        Observation(
            capability_id="dns.resolve",
            service_id="dns-primary",
            node_id="zwave-01",
            status=HealthStatus.HEALTHY,
            observed_at=observed_at,
            latency_ms=-1.0,
        )
