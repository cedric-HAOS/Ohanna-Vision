"""In-memory storage for immutable observations."""

from collections.abc import Iterable
from datetime import datetime
from uuid import UUID

from ohanna_vision.domain.observation import Observation


class DuplicateObservationError(ValueError):
    """Raised when an observation identifier already exists."""


class ObservationStore:
    """Store immutable observations without projecting domain state."""

    def __init__(self) -> None:
        """Initialize an empty observation store."""

        self._observations: list[Observation] = []
        self._observation_ids: set[UUID] = set()

    @property
    def observation_count(self) -> int:
        """Return the number of stored observations."""

        return len(self._observations)

    @property
    def observations(self) -> tuple[Observation, ...]:
        """Return observations in ingestion order."""

        return tuple(self._observations)

    def add(self, observation: Observation) -> Observation:
        """Store and return an observation."""

        if observation.observation_id in self._observation_ids:
            raise DuplicateObservationError(
                f"Observation {observation.observation_id} already exists."
            )

        self._observations.append(observation)
        self._observation_ids.add(observation.observation_id)

        return observation

    def add_many(
        self,
        observations: Iterable[Observation],
    ) -> tuple[Observation, ...]:
        """Store several observations in the provided order."""

        return tuple(self.add(observation) for observation in observations)

    def history(
        self,
        *,
        node_id: str | None = None,
        service_id: str | None = None,
        capability_id: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> tuple[Observation, ...]:
        """Return chronologically ordered observations matching filters."""

        self._validate_dates(since=since, until=until)

        observations = (
            observation
            for observation in self._observations
            if node_id is None or observation.node_id == node_id
        )
        observations = (
            observation
            for observation in observations
            if service_id is None or observation.service_id == service_id
        )
        observations = (
            observation
            for observation in observations
            if (
                capability_id is None
                or observation.capability_id == capability_id
            )
        )
        observations = (
            observation
            for observation in observations
            if since is None or observation.observed_at >= since
        )
        observations = (
            observation
            for observation in observations
            if until is None or observation.observed_at <= until
        )

        return tuple(
            sorted(
                observations,
                key=lambda observation: observation.observed_at,
            )
        )

    def clear(self) -> None:
        """Remove every stored observation."""

        self._observations.clear()
        self._observation_ids.clear()

    @staticmethod
    def _validate_dates(
        *,
        since: datetime | None,
        until: datetime | None,
    ) -> None:
        """Validate history date filters."""

        if since is not None and since.tzinfo is None:
            raise ValueError("since must be timezone-aware.")

        if until is not None and until.tzinfo is None:
            raise ValueError("until must be timezone-aware.")

        if since is not None and until is not None and since > until:
            raise ValueError("since must not be after until.")