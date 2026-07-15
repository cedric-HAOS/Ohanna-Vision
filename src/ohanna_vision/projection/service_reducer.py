"""Reducer building a service state from capability states."""

from collections.abc import Iterable

from ohanna_vision.domain.capability_state import CapabilityState
from ohanna_vision.domain.service_state import ServiceState


class EmptyServiceProjectionError(ValueError):
    """Raised when no capability state can be reduced."""


class MixedServiceCapabilitiesError(ValueError):
    """Raised when capabilities belong to different services."""


class ServiceReducer:
    """Reduce capability states to one service state."""

    def reduce(
        self,
        capabilities: Iterable[CapabilityState],
    ) -> ServiceState:
        """Build a service state from capability states."""

        values = tuple(
            sorted(
                capabilities,
                key=lambda capability: capability.capability_id,
            )
        )

        if not values:
            raise EmptyServiceProjectionError(
                "At least one capability state is required."
            )

        first = values[0]

        for capability in values[1:]:
            if (
                capability.node_id != first.node_id
                or capability.service_id != first.service_id
            ):
                raise MixedServiceCapabilitiesError(
                    "All capabilities must belong to the same service."
                )

        return ServiceState(
            service_id=first.service_id,
            node_id=first.node_id,
            capabilities=values,
        )
