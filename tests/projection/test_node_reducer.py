from datetime import UTC, datetime

import pytest

from ohanna_vision.domain import (
    CapabilityState,
    Health,
    HealthStatus,
    ServiceState,
)
from ohanna_vision.projection import (
    EmptyNodeProjectionError,
    MixedNodeServicesError,
    NodeReducer,
)


def make_service(
    service_id: str,
    *,
    node_id: str = "zwave-01",
) -> ServiceState:
    observed_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    capability = CapabilityState(
        capability_id=f"{service_id}.availability",
        service_id=service_id,
        node_id=node_id,
        health=Health(status=HealthStatus.HEALTHY),
        observed_at=observed_at,
        state_since=observed_at,
    )

    return ServiceState(
        service_id=service_id,
        node_id=node_id,
        capabilities=(capability,),
    )


def test_node_reducer_requires_service() -> None:
    with pytest.raises(EmptyNodeProjectionError):
        NodeReducer().reduce([])


def test_node_reducer_builds_node() -> None:
    node = NodeReducer().reduce(
        [
            make_service("dns-primary"),
            make_service("ntp-primary"),
        ]
    )

    assert node.node_id == "zwave-01"
    assert len(node.services) == 2


def test_node_reducer_rejects_mixed_nodes() -> None:
    with pytest.raises(MixedNodeServicesError):
        NodeReducer().reduce(
            [
                make_service("dns-primary"),
                make_service(
                    "mqtt-primary",
                    node_id="green-01",
                ),
            ]
        )
