"""Timeline model for an infrastructure capability."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from ohanna_vision.domain.health import HealthStatus
from ohanna_vision.timeline.state_period import StatePeriod
from ohanna_vision.timeline.timeline_validation import validate_periods


@dataclass(frozen=True, slots=True)
class CapabilityTimeline:
    """Represent the ordered state periods of one capability."""

    capability_id: str
    service_id: str
    node_id: str
    periods: tuple[StatePeriod, ...] = ()

    def __post_init__(self) -> None:
        """Validate capability timeline invariants."""

        if not self.capability_id.strip():
            raise ValueError("capability_id must not be empty.")

        if not self.service_id.strip():
            raise ValueError("service_id must not be empty.")

        if not self.node_id.strip():
            raise ValueError("node_id must not be empty.")

        validate_periods(self.periods)

    @property
    def is_empty(self) -> bool:
        """Return whether the timeline contains no period."""

        return not self.periods

    @property
    def first_period(self) -> StatePeriod | None:
        """Return the first known state period."""

        if not self.periods:
            return None

        return self.periods[0]

    @property
    def last_period(self) -> StatePeriod | None:
        """Return the last known state period."""

        if not self.periods:
            return None

        return self.periods[-1]

    @property
    def current_period(self) -> StatePeriod | None:
        """Return the currently open period, when one exists."""

        last_period = self.last_period

        if last_period is None or last_period.is_closed:
            return None

        return last_period

    @property
    def current_status(self) -> HealthStatus | None:
        """Return the currently active status."""

        current_period = self.current_period

        if current_period is None:
            return None

        return current_period.status

    @property
    def started_at(self) -> datetime | None:
        """Return the beginning of the timeline."""

        first_period = self.first_period

        if first_period is None:
            return None

        return first_period.started_at

    @property
    def ended_at(self) -> datetime | None:
        """Return the end of a fully closed timeline.

        An active timeline has no end date.
        """

        last_period = self.last_period

        if last_period is None or last_period.is_open:
            return None

        return last_period.ended_at

    @property
    def transition_count(self) -> int:
        """Return the number of status transitions."""

        return max(0, len(self.periods) - 1)

    @property
    def incident_periods(self) -> tuple[StatePeriod, ...]:
        """Return all non-healthy periods."""

        return tuple(
            period
            for period in self.periods
            if period.status is not HealthStatus.HEALTHY
        )

    @property
    def incident_count(self) -> int:
        """Return the number of non-healthy state periods."""

        return len(self.incident_periods)

    def period_at(self, instant: datetime) -> StatePeriod | None:
        """Return the period containing a given instant."""

        if instant.tzinfo is None:
            raise ValueError("instant must be timezone-aware.")

        return next(
            (
                period
                for period in self.periods
                if period.contains(instant)
            ),
            None,
        )

    def status_at(self, instant: datetime) -> HealthStatus | None:
        """Return the capability status at a given instant."""

        period = self.period_at(instant)

        if period is None:
            return None

        return period.status

    def current_duration(self, now: datetime) -> timedelta | None:
        """Return the duration of the currently active period."""

        current_period = self.current_period

        if current_period is None:
            return None

        return current_period.duration_at(now)

    def periods_with_status(
        self,
        status: HealthStatus,
    ) -> tuple[StatePeriod, ...]:
        """Return all periods matching a status."""

        return tuple(
            period
            for period in self.periods
            if period.status is status
        )

    def _validate_periods(self) -> None:
        """Validate ordering, continuity and open-period rules."""

        for index, period in enumerate(self.periods):
            if period.is_open and index != len(self.periods) - 1:
                raise ValueError(
                    "Only the last period may be open."
                )

        for previous, current in zip(
            self.periods,
            self.periods[1:],
            strict=False,
        ):
            if current.started_at < previous.started_at:
                raise ValueError(
                    "Periods must be ordered chronologically."
                )

            if previous.ended_at is None:
                raise ValueError(
                    "An open period cannot be followed by another period."
                )

            if current.started_at < previous.ended_at:
                raise ValueError(
                    "Periods must not overlap."
                )

            if current.started_at > previous.ended_at:
                raise ValueError(
                    "Periods must be contiguous."
                )

            if current.status is previous.status:
                raise ValueError(
                    "Consecutive periods must have different statuses."
                )