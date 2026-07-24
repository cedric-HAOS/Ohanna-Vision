"""Runtime retaining the current infrastructure timeline."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime

from ohana_vision.domain.observation import Observation
from ohana_vision.timeline.infrastructure_timeline import (
    InfrastructureTimeline,
)
from ohana_vision.timeline.timeline_engine import TimelineEngine


@dataclass(slots=True)
class TimelineRuntime:
    """Retain and refresh the current infrastructure timeline."""

    engine: TimelineEngine
    timeline: InfrastructureTimeline = field(
        default_factory=InfrastructureTimeline,
        init=False,
    )

    def build(
        self,
        observations: Iterable[Observation],
        *,
        until: datetime | None = None,
    ) -> InfrastructureTimeline:
        """Build an infrastructure timeline without retaining it."""
        return self.engine.build_infrastructure(
            observations,
            until=until,
        )

    def retain(
        self,
        timeline: InfrastructureTimeline,
    ) -> None:
        """Retain an already validated infrastructure timeline."""
        self.timeline = timeline

    def rebuild(
        self,
        observations: Iterable[Observation],
        *,
        until: datetime | None = None,
    ) -> InfrastructureTimeline:
        """Rebuild and retain the infrastructure timeline."""
        timeline = self.build(
            observations,
            until=until,
        )
        self.retain(timeline)

        return timeline

    def reset(self) -> None:
        """Reset the retained timeline."""
        self.timeline = InfrastructureTimeline()

    @property
    def node_count(self) -> int:
        """Return the number of retained node timelines."""
        return len(self.timeline.nodes)

    @property
    def service_count(self) -> int:
        """Return the number of retained service timelines."""
        return sum(len(node.services) for node in self.timeline.nodes)

    @property
    def capability_count(self) -> int:
        """Return the number of retained capability timelines."""
        return sum(
            len(service.capabilities)
            for node in self.timeline.nodes
            for service in node.services
        )

    @property
    def infrastructure_count(self) -> int:
        """Return whether an infrastructure timeline is retained."""
        return int(bool(self.timeline.nodes or self.timeline.periods))

    @property
    def empty(self) -> bool:
        """Return whether no timeline is currently retained."""
        return not self.timeline.nodes
