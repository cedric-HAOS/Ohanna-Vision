"""Tests for timeline API mapping."""

from datetime import UTC, datetime

from ohana_vision.domain import HealthStatus
from ohana_vision.timeline import (
    CapabilityTimeline,
    InfrastructureTimeline,
    NodeTimeline,
    ServiceTimeline,
    StatePeriod,
)
from ohana_vision.web.api.timeline_mapper import (
    map_capability_timeline,
    map_infrastructure_timeline,
    map_timeline_period,
)


def make_closed_period() -> StatePeriod:
    """Create one closed period."""
    return StatePeriod(
        status=HealthStatus.HEALTHY,
        started_at=datetime(
            2026,
            7,
            15,
            8,
            0,
            tzinfo=UTC,
        ),
        ended_at=datetime(
            2026,
            7,
            15,
            9,
            30,
            tzinfo=UTC,
        ),
    )


def test_mapper_exposes_closed_period_metadata() -> None:
    """A closed period must expose its duration."""
    response = map_timeline_period(
        make_closed_period(),
    )

    assert response.status is HealthStatus.HEALTHY
    assert response.started_at == datetime(
        2026,
        7,
        15,
        8,
        0,
        tzinfo=UTC,
    )
    assert response.ended_at == datetime(
        2026,
        7,
        15,
        9,
        30,
        tzinfo=UTC,
    )
    assert response.duration_seconds == 5400.0
    assert response.is_open is False


def test_mapper_exposes_open_period_metadata() -> None:
    """An open period must not invent an end or duration."""
    period = StatePeriod(
        status=HealthStatus.DEGRADED,
        started_at=datetime(
            2026,
            7,
            15,
            10,
            0,
            tzinfo=UTC,
        ),
    )

    response = map_timeline_period(period)

    assert response.status is HealthStatus.DEGRADED
    assert response.ended_at is None
    assert response.duration_seconds is None
    assert response.is_open is True


def test_mapper_preserves_capability_period_order() -> None:
    """Capability periods must remain chronologically ordered."""
    first = StatePeriod(
        status=HealthStatus.HEALTHY,
        started_at=datetime(
            2026,
            7,
            15,
            8,
            0,
            tzinfo=UTC,
        ),
        ended_at=datetime(
            2026,
            7,
            15,
            9,
            0,
            tzinfo=UTC,
        ),
    )
    second = StatePeriod(
        status=HealthStatus.DEGRADED,
        started_at=datetime(
            2026,
            7,
            15,
            9,
            0,
            tzinfo=UTC,
        ),
    )
    timeline = CapabilityTimeline(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="infra-01",
        periods=(first, second),
    )

    response = map_capability_timeline(timeline)

    assert [period.status for period in response.periods] == [
        HealthStatus.HEALTHY,
        HealthStatus.DEGRADED,
    ]


def test_mapper_preserves_complete_hierarchy() -> None:
    """Infrastructure mapping must preserve all hierarchy levels."""
    period = make_closed_period()
    capability = CapabilityTimeline(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="infra-01",
        periods=(period,),
    )
    service = ServiceTimeline(
        service_id="dns-primary",
        node_id="infra-01",
        capabilities=(capability,),
        periods=(period,),
    )
    node = NodeTimeline(
        node_id="infra-01",
        services=(service,),
        periods=(period,),
    )
    infrastructure = InfrastructureTimeline(
        nodes=(node,),
        periods=(period,),
    )

    response = map_infrastructure_timeline(
        infrastructure,
    )

    assert len(response.nodes) == 1
    assert response.nodes[0].node_id == "infra-01"
    assert response.nodes[0].services[0].service_id == "dns-primary"
    assert response.nodes[0].services[0].capabilities[0].capability_id == "dns.resolve"
    assert response.periods[0].duration_seconds == 5400.0


def test_timeline_period_schema_serializes_for_json() -> None:
    """Timeline schemas must produce a stable JSON contract."""
    response = map_timeline_period(
        make_closed_period(),
    )

    assert response.model_dump(mode="json") == {
        "status": "healthy",
        "started_at": "2026-07-15T08:00:00Z",
        "ended_at": "2026-07-15T09:30:00Z",
        "duration_seconds": 5400.0,
        "is_open": False,
    }
