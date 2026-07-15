"""Timeline model for an infrastructure service."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ohanna_vision.domain.health import HealthStatus
from ohanna_vision.timeline.capability_timeline import (
    CapabilityTimeline,
)
from ohanna_vision.timeline.state_period import StatePeriod
from ohanna_vision.timeline.timeline_validation import validate_periods


@dataclass(frozen=True, slots=True)
class ServiceTimeline:
    """Represent the temporal evolution of one service."""

    service_id: str
    node_id: str
    capabilities: tuple[CapabilityTimeline, ...] = ()
    periods: tuple[StatePeriod, ...] = ()

    def __post_init__(self) -> None:
        """Validate service timeline invariants."""

        if not self.service_id.strip():
            raise ValueError("service_id must not be empty.")

        if not self.node_id.strip():
            raise ValueError("node_id must not be empty.")

        capability_ids = tuple(
            capability.capability_id for capability in self.capabilities
        )

        if len(capability_ids) != len(set(capability_ids)):
            raise ValueError("capability identifiers must be unique.")

        for capability in self.capabilities:
            if capability.service_id != self.service_id:
                raise ValueError(
                    "Every capability timeline must belong to the service."
                )

            if capability.node_id != self.node_id:
                raise ValueError(
                    "Every capability timeline must belong to the service node."
                )

        validate_periods(self.periods)

    @property
    def is_empty(self) -> bool:
        """Return whether the timeline contains no period."""

        return not self.periods

    @property
    def current_period(self) -> StatePeriod | None:
        """Return the currently active service period."""

        if not self.periods or self.periods[-1].is_closed:
            return None

        return self.periods[-1]

    @property
    def current_status(self) -> HealthStatus | None:
        """Return the current service status."""

        period = self.current_period

        if period is None:
            return None

        return period.status

    @property
    def transition_count(self) -> int:
        """Return the number of service status transitions."""

        return max(0, len(self.periods) - 1)

    def capability(
        self,
        capability_id: str,
    ) -> CapabilityTimeline | None:
        """Return a capability timeline by identifier."""

        return next(
            (
                capability
                for capability in self.capabilities
                if capability.capability_id == capability_id
            ),
            None,
        )

    def status_at(
        self,
        instant: datetime,
    ) -> HealthStatus | None:
        """Return the service status at a given instant."""

        if instant.tzinfo is None:
            raise ValueError("instant must be timezone-aware.")

        period = next(
            (period for period in self.periods if period.contains(instant)),
            None,
        )

        if period is None:
            return None

        return period.status
