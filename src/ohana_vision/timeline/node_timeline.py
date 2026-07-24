"""Timeline model for an infrastructure node."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ohana_vision.domain.health import HealthStatus
from ohana_vision.timeline.service_timeline import ServiceTimeline
from ohana_vision.timeline.state_period import StatePeriod
from ohana_vision.timeline.timeline_validation import validate_periods


@dataclass(frozen=True, slots=True)
class NodeTimeline:
    """Represent the temporal evolution of one node."""

    node_id: str
    services: tuple[ServiceTimeline, ...] = ()
    periods: tuple[StatePeriod, ...] = ()

    def __post_init__(self) -> None:
        """Validate node timeline invariants."""

        if not self.node_id.strip():
            raise ValueError("node_id must not be empty.")

        service_ids = tuple(service.service_id for service in self.services)

        if len(service_ids) != len(set(service_ids)):
            raise ValueError("service identifiers must be unique.")

        for service in self.services:
            if service.node_id != self.node_id:
                raise ValueError("Every service timeline must belong to the node.")

        validate_periods(self.periods)

    @property
    def is_empty(self) -> bool:
        """Return whether the node timeline has no period."""

        return not self.periods

    @property
    def current_period(self) -> StatePeriod | None:
        """Return the currently active node period."""

        if not self.periods or self.periods[-1].is_closed:
            return None

        return self.periods[-1]

    @property
    def current_status(self) -> HealthStatus | None:
        """Return the current node status."""

        period = self.current_period

        if period is None:
            return None

        return period.status

    @property
    def transition_count(self) -> int:
        """Return the number of node status transitions."""

        return max(0, len(self.periods) - 1)

    def service(
        self,
        service_id: str,
    ) -> ServiceTimeline | None:
        """Return a service timeline by identifier."""

        return next(
            (service for service in self.services if service.service_id == service_id),
            None,
        )

    def status_at(
        self,
        instant: datetime,
    ) -> HealthStatus | None:
        """Return the node status at a given instant."""

        if instant.tzinfo is None:
            raise ValueError("instant must be timezone-aware.")

        period = next(
            (period for period in self.periods if period.contains(instant)),
            None,
        )

        if period is None:
            return None

        return period.status
