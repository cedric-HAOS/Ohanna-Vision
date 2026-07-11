"""Tests for TimelineRuntime."""

from __future__ import annotations

from datetime import UTC, datetime

from ohanna_vision.domain.health import HealthStatus
from ohanna_vision.domain.observation import Observation
from ohanna_vision.runtime.timeline_runtime import TimelineRuntime
from ohanna_vision.timeline.infrastructure_timeline import (
    InfrastructureTimeline,
)
from ohanna_vision.timeline.timeline_engine import TimelineEngine


def make_observation(
    *,
    capability_id: str = "dns.resolve",
    service_id: str = "dns-primary",
    node_id: str = "infra-01",
    status: HealthStatus = HealthStatus.HEALTHY,
    minute: int = 0,
) -> Observation:
    """Create an observation for timeline runtime tests."""
    return Observation(
        capability_id=capability_id,
        service_id=service_id,
        node_id=node_id,
        status=status,
        observed_at=datetime(
            2026,
            7,
            11,
            16,
            minute,
            tzinfo=UTC,
        ),
    )


def test_runtime_starts_with_empty_timeline() -> None:
    """The runtime must initially retain an empty timeline."""
    runtime = TimelineRuntime(
        engine=TimelineEngine(),
    )

    assert isinstance(runtime.timeline, InfrastructureTimeline)
    assert runtime.empty is True
    assert runtime.node_count == 0
    assert runtime.service_count == 0
    assert runtime.capability_count == 0


def test_runtime_rebuilds_infrastructure_timeline() -> None:
    """The runtime must retain the timeline built by its engine."""
    runtime = TimelineRuntime(
        engine=TimelineEngine(),
    )
    observations = [
        make_observation(),
    ]

    timeline = runtime.rebuild(observations)

    assert timeline is runtime.timeline
    assert runtime.empty is False


def test_runtime_exposes_timeline_counts() -> None:
    """The runtime must expose hierarchy counters."""
    runtime = TimelineRuntime(
        engine=TimelineEngine(),
    )
    observations = [
        make_observation(
            capability_id="dns.resolve",
            service_id="dns-primary",
            node_id="infra-01",
        ),
        make_observation(
            capability_id="dns.latency",
            service_id="dns-primary",
            node_id="infra-01",
        ),
        make_observation(
            capability_id="mqtt.connectivity",
            service_id="mqtt-primary",
            node_id="infra-01",
        ),
        make_observation(
            capability_id="dhcp.availability",
            service_id="dhcp-primary",
            node_id="infra-02",
        ),
    ]

    runtime.rebuild(observations)

    assert runtime.node_count == 2
    assert runtime.service_count == 3
    assert runtime.capability_count == 4


def test_runtime_rebuild_replaces_previous_timeline() -> None:
    """A rebuild must replace the previously retained projection."""
    runtime = TimelineRuntime(
        engine=TimelineEngine(),
    )

    first = runtime.rebuild(
        [
            make_observation(
                node_id="infra-01",
            ),
        ]
    )
    second = runtime.rebuild(
        [
            make_observation(
                node_id="infra-02",
                service_id="mqtt-primary",
                capability_id="mqtt.connectivity",
            ),
        ]
    )

    assert second is runtime.timeline
    assert second is not first
    assert runtime.node_count == 1
    assert runtime.timeline.nodes[0].node_id == "infra-02"


def test_runtime_rebuilds_empty_timeline_without_observations() -> None:
    """An empty observation collection must produce an empty timeline."""
    runtime = TimelineRuntime(
        engine=TimelineEngine(),
    )

    timeline = runtime.rebuild([])

    assert timeline is runtime.timeline
    assert runtime.empty is True


def test_runtime_reset_clears_retained_timeline() -> None:
    """Reset must replace the retained projection with an empty one."""
    runtime = TimelineRuntime(
        engine=TimelineEngine(),
    )
    runtime.rebuild(
        [
            make_observation(),
        ]
    )

    runtime.reset()

    assert runtime.empty is True
    assert runtime.node_count == 0
    assert runtime.service_count == 0
    assert runtime.capability_count == 0