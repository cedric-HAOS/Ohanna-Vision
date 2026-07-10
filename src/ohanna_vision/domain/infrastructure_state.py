"""Current state of the complete infrastructure."""

from dataclasses import dataclass
from datetime import datetime

from ohanna_vision.domain.health import Health, aggregate_health
from ohanna_vision.domain.node_state import NodeState
from ohanna_vision.domain.service_state import ServiceState


@dataclass(frozen=True, slots=True)
class InfrastructureState:
    """Represent the latest known state of the infrastructure."""

    nodes: tuple[NodeState, ...]

    def __post_init__(self) -> None:
        """Validate infrastructure state invariants."""

        node_ids = tuple(node.node_id for node in self.nodes)

        if len(node_ids) != len(set(node_ids)):
            raise ValueError("node identifiers must be unique.")

    @property
    def health(self) -> Health:
        """Return the aggregated infrastructure health."""

        return aggregate_health(node.health for node in self.nodes)

    @property
    def last_updated_at(self) -> datetime | None:
        """Return the latest known infrastructure update."""

        dates = tuple(
            node.last_updated_at
            for node in self.nodes
            if node.last_updated_at is not None
        )

        if not dates:
            return None

        return max(dates)

    @property
    def services(self) -> tuple[ServiceState, ...]:
        """Return all infrastructure services."""

        return tuple(
            service
            for node in self.nodes
            for service in node.services
        )

    @property
    def capability_count(self) -> int:
        """Return the number of known capabilities."""

        return sum(
            len(service.capabilities)
            for service in self.services
        )

    def node(self, node_id: str) -> NodeState | None:
        """Return a node by identifier."""

        return next(
            (node for node in self.nodes if node.node_id == node_id),
            None,
        )

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