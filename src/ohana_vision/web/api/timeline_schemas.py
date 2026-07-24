"""API schemas for infrastructure timelines."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from ohana_vision.domain import HealthStatus


class TimelinePeriodResponse(BaseModel):
    """Represent one continuous health period in the API."""

    model_config = ConfigDict(frozen=True)

    status: HealthStatus
    started_at: datetime
    ended_at: datetime | None
    duration_seconds: float | None
    is_open: bool


class CapabilityTimelineResponse(BaseModel):
    """Represent one capability timeline in the API."""

    model_config = ConfigDict(frozen=True)

    capability_id: str
    service_id: str
    node_id: str
    periods: tuple[TimelinePeriodResponse, ...]


class ServiceTimelineResponse(BaseModel):
    """Represent one service timeline in the API."""

    model_config = ConfigDict(frozen=True)

    service_id: str
    node_id: str
    capabilities: tuple[CapabilityTimelineResponse, ...]
    periods: tuple[TimelinePeriodResponse, ...]


class NodeTimelineResponse(BaseModel):
    """Represent one node timeline in the API."""

    model_config = ConfigDict(frozen=True)

    node_id: str
    services: tuple[ServiceTimelineResponse, ...]
    periods: tuple[TimelinePeriodResponse, ...]


class InfrastructureTimelineResponse(BaseModel):
    """Represent the complete infrastructure timeline."""

    model_config = ConfigDict(frozen=True)

    nodes: tuple[NodeTimelineResponse, ...]
    periods: tuple[TimelinePeriodResponse, ...]
