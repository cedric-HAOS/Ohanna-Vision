"""Reducer building an infrastructure state from node states."""

from collections.abc import Iterable

from ohanna_vision.domain.infrastructure_state import InfrastructureState
from ohanna_vision.domain.node_state import NodeState


class InfrastructureReducer:
    """Reduce node states to an infrastructure state."""

    def reduce(
        self,
        nodes: Iterable[NodeState],
    ) -> InfrastructureState:
        """Build an infrastructure state from node states."""

        values = tuple(
            sorted(
                nodes,
                key=lambda node: node.node_id,
            )
        )

        return InfrastructureState(nodes=values)
