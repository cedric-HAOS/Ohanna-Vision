"""Timeline model for the complete infrastructure."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ohanna_vision.domain.health import HealthStatus
from ohanna_vision.timeline.node_timeline import NodeTimeline
from ohanna_vision.timeline.state_period import StatePeriod
from ohanna_vision.timeline.timeline_validation import validate_periods


@dataclass(frozen=True, slots=True)
class InfrastructureTimeline:
    """Represent the temporal evolution of the infrastructure."""

    nodes: tuple[NodeTimeline, ...] = ()
    periods: tuple[StatePeriod, ...] = ()

    def __post_init__(self) -> None:
        """Validate infrastructure timeline invariants."""

        node_ids = tuple(node.node_id for node in self.nodes)

        if len(node_ids) != len(set(node_ids)):
            raise ValueError("node identifiers must be unique.")

        validate_periods(self.periods)

    @property
    def is_empty(self) -> bool:
        """Return whether the infrastructure has no timeline period."""

        return not self.periods

    @property
    def current_period(self) -> StatePeriod | None:
        """Return the currently active infrastructure period."""

        if not self.periods or self.periods[-1].is_closed:
            return None

        return self.periods[-1]

    @property
    def current_status(self) -> HealthStatus | None:
        """Return the current infrastructure status."""

        period = self.current_period

        if period is None:
            return None

        return period.status

    @property
    def transition_count(self) -> int:
        """Return the number of infrastructure transitions."""

        return max(0, len(self.periods) - 1)

    def node(self, node_id: str) -> NodeTimeline | None:
        """Return a node timeline by identifier."""

        return next(
            (node for node in self.nodes if node.node_id == node_id),
            None,
        )

    def status_at(
        self,
        instant: datetime,
    ) -> HealthStatus | None:
        """Return the infrastructure status at a given instant."""

        if instant.tzinfo is None:
            raise ValueError("instant must be timezone-aware.")

        period = next(
            (period for period in self.periods if period.contains(instant)),
            None,
        )

        if period is None:
            return None

        return period.status
