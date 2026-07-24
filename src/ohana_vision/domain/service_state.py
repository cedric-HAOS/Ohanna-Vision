"""Current state of an infrastructure service."""

from dataclasses import dataclass
from datetime import datetime

from ohana_vision.domain.capability_state import CapabilityState
from ohana_vision.domain.health import Health, aggregate_health


@dataclass(frozen=True, slots=True)
class ServiceState:
    """Represent the current state of a service."""

    service_id: str
    node_id: str
    capabilities: tuple[CapabilityState, ...]

    def __post_init__(self) -> None:
        """Validate service state invariants."""

        if not self.service_id.strip():
            raise ValueError("service_id must not be empty.")

        if not self.node_id.strip():
            raise ValueError("node_id must not be empty.")

        for capability in self.capabilities:
            if capability.service_id != self.service_id:
                raise ValueError("Every capability must belong to the service.")

            if capability.node_id != self.node_id:
                raise ValueError("Every capability must belong to the service node.")

    @property
    def health(self) -> Health:
        """Return the aggregated health of the service."""

        return aggregate_health(capability.health for capability in self.capabilities)

    @property
    def last_updated_at(self) -> datetime | None:
        """Return the date of the most recent capability state."""

        if not self.capabilities:
            return None

        return max(capability.observed_at for capability in self.capabilities)

    def capability(self, capability_id: str) -> CapabilityState | None:
        """Return a capability by identifier."""

        return next(
            (
                capability
                for capability in self.capabilities
                if capability.capability_id == capability_id
            ),
            None,
        )
