"""Immutable snapshot of the backend runtime."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ohanna_vision.runtime.backend_runtime_state import (
    BackendRuntimeState,
)
from ohanna_vision.runtime.runtime_statistics import RuntimeStatistics


@dataclass(frozen=True, slots=True)
class RuntimeSnapshot:
    """Immutable representation of the backend runtime."""

    state: BackendRuntimeState
    statistics: RuntimeStatistics
    generated_at: datetime
    observations_stored: int = 0
    service_timelines: int = 0
    node_timelines: int = 0
    infrastructure_timelines: int = 0

    def __post_init__(self) -> None:
        """Validate snapshot counters."""

        counters = {
            "observations_stored": self.observations_stored,
            "service_timelines": self.service_timelines,
            "node_timelines": self.node_timelines,
            "infrastructure_timelines": self.infrastructure_timelines,
        }

        for name, value in counters.items():
            if value < 0:
                raise ValueError(f"{name} cannot be negative")

    @property
    def running(self) -> bool:
        """Return whether the backend is running."""

        return self.state is BackendRuntimeState.RUNNING

    @property
    def healthy(self) -> bool:
        """Return whether the backend is operational."""

        return self.state.healthy

    @property
    def timeline_count(self) -> int:
        """Return the total number of timelines."""

        return (
            self.service_timelines
            + self.node_timelines
            + self.infrastructure_timelines
        )

    @property
    def has_observations(self) -> bool:
        """Return whether observations are currently stored."""

        return self.observations_stored > 0