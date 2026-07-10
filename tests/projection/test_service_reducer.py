from datetime import UTC, datetime

import pytest

from ohanna_vision.domain import (
    CapabilityState,
    Health,
    HealthStatus,
)
from ohanna_vision.projection import (
    EmptyServiceProjectionError,
    MixedServiceCapabilitiesError,
    ServiceReducer,
)


def make_capability(
    capability_id: str,
    *,
    service_id: str = "dns-primary",
) -> CapabilityState:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    return CapabilityState(
        capability_id=capability_id,
        service_id=service_id,
        node_id="zwave-01",
        health=Health(status=HealthStatus.HEALTHY),
        observed_at=observed_at,
        state_since=observed_at,
    )


def test_service_reducer_requires_capability() -> None:
    with pytest.raises(EmptyServiceProjectionError):
        ServiceReducer().reduce([])


def test_service_reducer_builds_service() -> None:
    service = ServiceReducer().reduce(
        [
            make_capability("dns.resolve"),
            make_capability("dns.latency"),
        ]
    )

    assert service.service_id == "dns-primary"
    assert len(service.capabilities) == 2


def test_service_reducer_rejects_mixed_services() -> None:
    with pytest.raises(MixedServiceCapabilitiesError):
        ServiceReducer().reduce(
            [
                make_capability("dns.resolve"),
                make_capability(
                    "mqtt.connect",
                    service_id="mqtt-primary",
                ),
            ]
        )