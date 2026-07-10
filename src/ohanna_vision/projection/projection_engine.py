"""Projection engine orchestrating infrastructure reducers."""

from collections import defaultdict
from collections.abc import Iterable
from datetime import datetime

from ohanna_vision.domain.capability_state import CapabilityState
from ohanna_vision.domain.infrastructure_state import InfrastructureState
from ohanna_vision.domain.node_state import NodeState
from ohanna_vision.domain.observation import Observation
from ohanna_vision.domain.service_state import ServiceState
from ohanna_vision.projection.capability_reducer import CapabilityReducer
from ohanna_vision.projection.infrastructure_reducer import (
    InfrastructureReducer,
)
from ohanna_vision.projection.node_reducer import NodeReducer
from ohanna_vision.projection.service_reducer import ServiceReducer

type CapabilityKey = tuple[str, str, str]
type ServiceKey = tuple[str, str]


class ProjectionEngine:
    """Project observations into an infrastructure state."""

    def __init__(
        self,
        *,
        capability_reducer: CapabilityReducer | None = None,
        service_reducer: ServiceReducer | None = None,
        node_reducer: NodeReducer | None = None,
        infrastructure_reducer: InfrastructureReducer | None = None,
    ) -> None:
        """Initialize the engine with optional reducer dependencies."""

        self._capability_reducer = (
            capability_reducer or CapabilityReducer()
        )
        self._service_reducer = service_reducer or ServiceReducer()
        self._node_reducer = node_reducer or NodeReducer()
        self._infrastructure_reducer = (
            infrastructure_reducer or InfrastructureReducer()
        )

    def project(
        self,
        observations: Iterable[Observation],
        *,
        at: datetime | None = None,
    ) -> InfrastructureState:
        """Project observations into an infrastructure state.

        When ``at`` is provided, observations occurring after that instant
        are ignored. This allows reconstruction of a historical state.
        """

        self._validate_projection_date(at)

        selected = tuple(
            observation
            for observation in observations
            if at is None or observation.observed_at <= at
        )

        capability_states = self._project_capabilities(selected)
        service_states = self._project_services(capability_states)
        node_states = self._project_nodes(service_states)

        return self._infrastructure_reducer.reduce(node_states)

    def _project_capabilities(
        self,
        observations: tuple[Observation, ...],
    ) -> tuple[CapabilityState, ...]:
        """Project observations grouped by capability."""

        grouped: dict[
            CapabilityKey,
            list[Observation],
        ] = defaultdict(list)

        for observation in observations:
            key = (
                observation.node_id,
                observation.service_id,
                observation.capability_id,
            )
            grouped[key].append(observation)

        return tuple(
            self._capability_reducer.reduce(grouped[key])
            for key in sorted(grouped)
        )

    def _project_services(
        self,
        capabilities: tuple[CapabilityState, ...],
    ) -> tuple[ServiceState, ...]:
        """Project capability states grouped by service."""

        grouped: dict[
            ServiceKey,
            list[CapabilityState],
        ] = defaultdict(list)

        for capability in capabilities:
            key = (
                capability.node_id,
                capability.service_id,
            )
            grouped[key].append(capability)

        return tuple(
            self._service_reducer.reduce(grouped[key])
            for key in sorted(grouped)
        )

    def _project_nodes(
        self,
        services: tuple[ServiceState, ...],
    ) -> tuple[NodeState, ...]:
        """Project service states grouped by node."""

        grouped: dict[str, list[ServiceState]] = defaultdict(list)

        for service in services:
            grouped[service.node_id].append(service)

        return tuple(
            self._node_reducer.reduce(grouped[node_id])
            for node_id in sorted(grouped)
        )

    @staticmethod
    def _validate_projection_date(at: datetime | None) -> None:
        """Validate the optional historical projection date."""

        if at is not None and at.tzinfo is None:
            raise ValueError("at must be timezone-aware.")