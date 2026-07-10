"""Current state of an infrastructure node."""

from dataclasses import dataclass
from datetime import datetime

from ohanna_vision.domain.health import Health, aggregate_health
from ohanna_vision.domain.service_state import ServiceState


@dataclass(frozen=True, slots=True)
class NodeState:
    """Represent the current state of an infrastructure node."""

    node_id: str
    services: tuple[ServiceState, ...]

    def __post_init__(self) -> None:
        """Validate node state invariants."""

        if not self.node_id.strip():
            raise ValueError("node_id must not be empty.")

        for service in self.services:
            if service.node_id != self.node_id:
                raise ValueError(
                    "Every service must belong to the node."
                )

    @property
    def health(self) -> Health:
        """Return the aggregated health of the node."""

        return aggregate_health(service.health for service in self.services)

    @property
    def last_updated_at(self) -> datetime | None:
        """Return the latest update date of the node."""

        dates = tuple(
            service.last_updated_at
            for service in self.services
            if service.last_updated_at is not None
        )

        if not dates:
            return None

        return max(dates)

    def service(self, service_id: str) -> ServiceState | None:
        """Return a service by identifier."""

        return next(
            (
                service
                for service in self.services
                if service.service_id == service_id
            ),
            None,
        )