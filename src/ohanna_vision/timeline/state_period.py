"""State period model used by infrastructure timelines."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from ohanna_vision.domain.health import HealthStatus


@dataclass(frozen=True, slots=True)
class StatePeriod:
    """Represent a continuous period spent in one health status."""

    status: HealthStatus
    started_at: datetime
    ended_at: datetime | None = None

    def __post_init__(self) -> None:
        """Validate state period invariants."""

        if self.started_at.tzinfo is None:
            raise ValueError("started_at must be timezone-aware.")

        if self.ended_at is not None:
            if self.ended_at.tzinfo is None:
                raise ValueError("ended_at must be timezone-aware.")

            if self.ended_at < self.started_at:
                raise ValueError(
                    "ended_at must not be before started_at."
                )

    @property
    def is_open(self) -> bool:
        """Return whether the period is still in progress."""

        return self.ended_at is None

    @property
    def is_closed(self) -> bool:
        """Return whether the period has a known end date."""

        return self.ended_at is not None

    @property
    def duration(self) -> timedelta | None:
        """Return the duration of a closed period.

        Open periods do not have a fixed duration and therefore return None.
        Use ``duration_at`` to calculate their duration at a given instant.
        """

        if self.ended_at is None:
            return None

        return self.ended_at - self.started_at

    @property
    def duration_seconds(self) -> float | None:
        """Return the duration of a closed period in seconds."""

        duration = self.duration

        if duration is None:
            return None

        return duration.total_seconds()

    def duration_at(self, instant: datetime) -> timedelta:
        """Return the period duration at a given instant.

        For a closed period, its fixed duration is returned.

        For an open period, the duration is calculated between ``started_at``
        and the provided instant.
        """

        if instant.tzinfo is None:
            raise ValueError("instant must be timezone-aware.")

        if instant < self.started_at:
            raise ValueError(
                "instant must not be before started_at."
            )

        if self.ended_at is not None:
            return self.ended_at - self.started_at

        return instant - self.started_at

    def contains(self, instant: datetime) -> bool:
        """Return whether an instant belongs to the period.

        Periods use a half-open interval:

        ``started_at <= instant < ended_at``

        An open period contains every instant from its start onward.
        """

        if instant.tzinfo is None:
            raise ValueError("instant must be timezone-aware.")

        if instant < self.started_at:
            return False

        if self.ended_at is None:
            return True

        return instant < self.ended_at

    def close(self, ended_at: datetime) -> StatePeriod:
        """Return a closed copy of the period."""

        if self.ended_at is not None:
            raise ValueError("A closed period cannot be closed again.")

        return StatePeriod(
            status=self.status,
            started_at=self.started_at,
            ended_at=ended_at,
        )