from datetime import UTC, datetime, timedelta

import pytest

from ohanna_vision.domain import (
    CapabilityState,
    Health,
    HealthStatus,
    ServiceState,
)


def make_capability(
    capability_id: str,
    status: HealthStatus,
    observed_at: datetime,
) -> CapabilityState:
    return CapabilityState(
        capability_id=capability_id,
        service_id="dns-primary",
        node_id="zwave-01",
        health=Health(status=status),
        observed_at=observed_at,
        state_since=observed_at,
    )


def test_service_state_aggregates_capability_health() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    service = ServiceState(
        service_id="dns-primary",
        node_id="zwave-01",
        capabilities=(
            make_capability(
                "dns.resolve",
                HealthStatus.HEALTHY,
                observed_at,
            ),
            make_capability(
                "dns.latency",
                HealthStatus.DEGRADED,
                observed_at,
            ),
        ),
    )

    assert service.health.status is HealthStatus.DEGRADED


def test_service_state_returns_latest_update() -> None:
    first_date = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    second_date = first_date + timedelta(minutes=5)

    service = ServiceState(
        service_id="dns-primary",
        node_id="zwave-01",
        capabilities=(
            make_capability(
                "dns.resolve",
                HealthStatus.HEALTHY,
                first_date,
            ),
            make_capability(
                "dns.latency",
                HealthStatus.HEALTHY,
                second_date,
            ),
        ),
    )

    assert service.last_updated_at == second_date


def test_service_state_finds_capability() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    capability = make_capability(
        "dns.resolve",
        HealthStatus.HEALTHY,
        observed_at,
    )

    service = ServiceState(
        service_id="dns-primary",
        node_id="zwave-01",
        capabilities=(capability,),
    )

    assert service.capability("dns.resolve") is capability
    assert service.capability("unknown") is None


def test_service_state_rejects_foreign_capability() -> None:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    capability = CapabilityState(
        capability_id="mqtt.connect",
        service_id="mqtt-primary",
        node_id="zwave-01",
        health=Health(status=HealthStatus.HEALTHY),
        observed_at=observed_at,
        state_since=observed_at,
    )

    with pytest.raises(
        ValueError,
        match="Every capability must belong to the service",
    ):
        ServiceState(
            service_id="dns-primary",
            node_id="zwave-01",
            capabilities=(capability,),
        )
