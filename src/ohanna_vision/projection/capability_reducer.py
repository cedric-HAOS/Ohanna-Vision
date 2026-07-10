"""Reducer building a capability state from observations."""

from collections.abc import Iterable
from datetime import datetime

from ohanna_vision.domain.capability_state import CapabilityState
from ohanna_vision.domain.health import Health
from ohanna_vision.domain.observation import Observation


class EmptyCapabilityProjectionError(ValueError):
    """Raised when no observation can be reduced."""


class MixedCapabilityObservationsError(ValueError):
    """Raised when observations belong to different capabilities."""


class CapabilityReducer:
    """Reduce capability observations to their latest known state."""

    def reduce(
        self,
        observations: Iterable[Observation],
    ) -> CapabilityState:
        """Build a capability state from chronological facts."""

        ordered = tuple(
            sorted(
                observations,
                key=lambda observation: observation.observed_at,
            )
        )

        if not ordered:
            raise EmptyCapabilityProjectionError(
                "At least one observation is required."
            )

        self._validate_same_capability(ordered)

        latest = ordered[-1]
        state_since = self._resolve_state_since(ordered)

        return CapabilityState(
            capability_id=latest.capability_id,
            service_id=latest.service_id,
            node_id=latest.node_id,
            health=Health(
                status=latest.status,
                reason=latest.message,
            ),
            observed_at=latest.observed_at,
            state_since=state_since,
            message=latest.message,
            latency_ms=latest.latency_ms,
            metadata=latest.metadata,
        )

    @staticmethod
    def _validate_same_capability(
        observations: tuple[Observation, ...],
    ) -> None:
        """Ensure all facts describe the same capability."""

        first = observations[0]
        expected_key = (
            first.node_id,
            first.service_id,
            first.capability_id,
        )

        for observation in observations[1:]:
            key = (
                observation.node_id,
                observation.service_id,
                observation.capability_id,
            )

            if key != expected_key:
                raise MixedCapabilityObservationsError(
                    "All observations must belong to the same capability."
                )

    @staticmethod
    def _resolve_state_since(
        observations: tuple[Observation, ...],
    ) -> datetime:
        """Return when the latest uninterrupted status began."""

        latest_status = observations[-1].status
        state_since = observations[-1].observed_at

        for observation in reversed(observations[:-1]):
            if observation.status is not latest_status:
                break

            state_since = observation.observed_at

        return state_since