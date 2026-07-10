"""Reducer building a node state from service states."""

from collections.abc import Iterable

from ohanna_vision.domain.node_state import NodeState
from ohanna_vision.domain.service_state import ServiceState


class EmptyNodeProjectionError(ValueError):
    """Raised when no service state can be reduced."""


class MixedNodeServicesError(ValueError):
    """Raised when services belong to different nodes."""


class NodeReducer:
    """Reduce service states to one node state."""

    def reduce(
        self,
        services: Iterable[ServiceState],
    ) -> NodeState:
        """Build a node state from service states."""

        values = tuple(
            sorted(
                services,
                key=lambda service: service.service_id,
            )
        )

        if not values:
            raise EmptyNodeProjectionError(
                "At least one service state is required."
            )

        node_id = values[0].node_id

        for service in values[1:]:
            if service.node_id != node_id:
                raise MixedNodeServicesError(
                    "All services must belong to the same node."
                )

        return NodeState(
            node_id=node_id,
            services=values,
        )