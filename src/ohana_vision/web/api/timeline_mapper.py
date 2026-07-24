"""Map timeline domain models to API response schemas."""

from ohana_vision.timeline import (
    CapabilityTimeline,
    InfrastructureTimeline,
    NodeTimeline,
    ServiceTimeline,
    StatePeriod,
)
from ohana_vision.web.api.timeline_schemas import (
    CapabilityTimelineResponse,
    InfrastructureTimelineResponse,
    NodeTimelineResponse,
    ServiceTimelineResponse,
    TimelinePeriodResponse,
)


def map_timeline_period(
    period: StatePeriod,
) -> TimelinePeriodResponse:
    """Map one domain state period to its API representation."""
    return TimelinePeriodResponse(
        status=period.status,
        started_at=period.started_at,
        ended_at=period.ended_at,
        duration_seconds=period.duration_seconds,
        is_open=period.is_open,
    )


def map_capability_timeline(
    timeline: CapabilityTimeline,
) -> CapabilityTimelineResponse:
    """Map one capability timeline."""
    return CapabilityTimelineResponse(
        capability_id=timeline.capability_id,
        service_id=timeline.service_id,
        node_id=timeline.node_id,
        periods=tuple(map_timeline_period(period) for period in timeline.periods),
    )


def map_service_timeline(
    timeline: ServiceTimeline,
) -> ServiceTimelineResponse:
    """Map one service timeline."""
    return ServiceTimelineResponse(
        service_id=timeline.service_id,
        node_id=timeline.node_id,
        capabilities=tuple(
            map_capability_timeline(capability) for capability in timeline.capabilities
        ),
        periods=tuple(map_timeline_period(period) for period in timeline.periods),
    )


def map_node_timeline(
    timeline: NodeTimeline,
) -> NodeTimelineResponse:
    """Map one node timeline."""
    return NodeTimelineResponse(
        node_id=timeline.node_id,
        services=tuple(map_service_timeline(service) for service in timeline.services),
        periods=tuple(map_timeline_period(period) for period in timeline.periods),
    )


def map_infrastructure_timeline(
    timeline: InfrastructureTimeline,
) -> InfrastructureTimelineResponse:
    """Map the complete infrastructure timeline."""
    return InfrastructureTimelineResponse(
        nodes=tuple(map_node_timeline(node) for node in timeline.nodes),
        periods=tuple(map_timeline_period(period) for period in timeline.periods),
    )
