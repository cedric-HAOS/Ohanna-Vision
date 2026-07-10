"""Engine building infrastructure timelines from observations."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable, Sequence
from datetime import datetime

from ohanna_vision.domain.health import HealthStatus
from ohanna_vision.domain.observation import Observation
from ohanna_vision.timeline.capability_timeline import (
    CapabilityTimeline,
)
from ohanna_vision.timeline.infrastructure_timeline import (
    InfrastructureTimeline,
)
from ohanna_vision.timeline.node_timeline import NodeTimeline
from ohanna_vision.timeline.service_timeline import ServiceTimeline
from ohanna_vision.timeline.state_period import StatePeriod

type CapabilityKey = tuple[str, str, str]
type ServiceKey = tuple[str, str]


_STATUS_PRIORITY: dict[HealthStatus, int] = {
    HealthStatus.HEALTHY: 0,
    HealthStatus.UNKNOWN: 1,
    HealthStatus.STALE: 2,
    HealthStatus.DEGRADED: 3,
    HealthStatus.UNAVAILABLE: 4,
}


class MixedTimelineObservationsError(ValueError):
    """Raised when observations target different capabilities."""


class ConflictingTimelineObservationsError(ValueError):
    """Raised when simultaneous observations have different statuses."""


class TimelineEngine:
    """Build timelines from immutable observations."""

    def build(
        self,
        observations: Iterable[Observation],
        *,
        until: datetime | None = None,
    ) -> CapabilityTimeline:
        """Build a timeline for one capability."""

        self._validate_until(until)

        selected = tuple(
            observation
            for observation in observations
            if until is None or observation.observed_at <= until
        )

        if not selected:
            raise ValueError(
                "At least one observation is required to build a timeline."
            )

        self._validate_same_capability(selected)

        ordered = self._sort_observations(selected)
        self._validate_simultaneous_observations(ordered)

        first = ordered[0]

        return CapabilityTimeline(
            capability_id=first.capability_id,
            service_id=first.service_id,
            node_id=first.node_id,
            periods=self._build_periods(
                ordered,
                until=until,
            ),
        )

    def build_infrastructure(
        self,
        observations: Iterable[Observation],
        *,
        until: datetime | None = None,
    ) -> InfrastructureTimeline:
        """Build the complete infrastructure timeline hierarchy."""

        self._validate_until(until)

        selected = tuple(
            observation
            for observation in observations
            if until is None or observation.observed_at <= until
        )

        if not selected:
            return InfrastructureTimeline()

        capabilities = self._build_capability_timelines(
            selected,
            until=until,
        )
        services = self._build_service_timelines(capabilities)
        nodes = self._build_node_timelines(services)

        return InfrastructureTimeline(
            nodes=nodes,
            periods=self._aggregate_timelines(
                nodes,
            ),
        )

    def _build_capability_timelines(
        self,
        observations: tuple[Observation, ...],
        *,
        until: datetime | None,
    ) -> tuple[CapabilityTimeline, ...]:
        """Build all capability timelines."""

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
            self.build(
                grouped[key],
                until=until,
            )
            for key in sorted(grouped)
        )

    def _build_service_timelines(
        self,
        capabilities: tuple[CapabilityTimeline, ...],
    ) -> tuple[ServiceTimeline, ...]:
        """Build service timelines from capability timelines."""

        grouped: dict[
            ServiceKey,
            list[CapabilityTimeline],
        ] = defaultdict(list)

        for capability in capabilities:
            key = (
                capability.node_id,
                capability.service_id,
            )
            grouped[key].append(capability)

        timelines: list[ServiceTimeline] = []

        for key in sorted(grouped):
            node_id, service_id = key
            children = tuple(
                sorted(
                    grouped[key],
                    key=lambda item: item.capability_id,
                )
            )

            timelines.append(
                ServiceTimeline(
                    service_id=service_id,
                    node_id=node_id,
                    capabilities=children,
                    periods=self._aggregate_timelines(children),
                )
            )

        return tuple(timelines)

    def _build_node_timelines(
        self,
        services: tuple[ServiceTimeline, ...],
    ) -> tuple[NodeTimeline, ...]:
        """Build node timelines from service timelines."""

        grouped: dict[str, list[ServiceTimeline]] = defaultdict(list)

        for service in services:
            grouped[service.node_id].append(service)

        timelines: list[NodeTimeline] = []

        for node_id in sorted(grouped):
            children = tuple(
                sorted(
                    grouped[node_id],
                    key=lambda item: item.service_id,
                )
            )

            timelines.append(
                NodeTimeline(
                    node_id=node_id,
                    services=children,
                    periods=self._aggregate_timelines(children),
                )
            )

        return tuple(timelines)

    @staticmethod
    def _aggregate_timelines(
        timelines: Sequence[
            CapabilityTimeline | ServiceTimeline | NodeTimeline
        ],
    ) -> tuple[StatePeriod, ...]:
        """Aggregate child timelines using the most severe active status."""

        child_periods = tuple(
            period
            for timeline in timelines
            for period in timeline.periods
        )

        if not child_periods:
            return ()

        boundaries = {
            period.started_at
            for period in child_periods
        }
        boundaries.update(
            period.ended_at
            for period in child_periods
            if period.ended_at is not None
        )

        ordered_boundaries = tuple(sorted(boundaries))
        periods: list[StatePeriod] = []

        for index, started_at in enumerate(ordered_boundaries):
            statuses = tuple(
                period.status
                for period in child_periods
                if period.contains(started_at)
            )

            if not statuses:
                continue

            status = max(
                statuses,
                key=lambda value: _STATUS_PRIORITY[value],
            )

            ended_at = (
                ordered_boundaries[index + 1]
                if index + 1 < len(ordered_boundaries)
                else None
            )

            if (
                periods
                and periods[-1].status is status
                and periods[-1].ended_at == started_at
            ):
                previous = periods.pop()

                periods.append(
                    StatePeriod(
                        status=status,
                        started_at=previous.started_at,
                        ended_at=ended_at,
                    )
                )
                continue

            periods.append(
                StatePeriod(
                    status=status,
                    started_at=started_at,
                    ended_at=ended_at,
                )
            )

        return tuple(periods)

    @staticmethod
    def _sort_observations(
        observations: tuple[Observation, ...],
    ) -> tuple[Observation, ...]:
        """Return observations in deterministic chronological order."""

        return tuple(
            sorted(
                observations,
                key=lambda observation: (
                    observation.observed_at,
                    str(observation.observation_id),
                ),
            )
        )

    @staticmethod
    def _validate_until(until: datetime | None) -> None:
        """Validate the optional timeline end date."""

        if until is not None and until.tzinfo is None:
            raise ValueError("until must be timezone-aware.")

    @staticmethod
    def _validate_same_capability(
        observations: tuple[Observation, ...],
    ) -> None:
        """Ensure all observations describe the same capability."""

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
                raise MixedTimelineObservationsError(
                    "All observations must belong to the same capability."
                )

    @staticmethod
    def _validate_simultaneous_observations(
        observations: tuple[Observation, ...],
    ) -> None:
        """Reject contradictory statuses observed simultaneously."""

        previous = observations[0]

        for current in observations[1:]:
            if (
                current.observed_at == previous.observed_at
                and current.status is not previous.status
            ):
                raise ConflictingTimelineObservationsError(
                    "Observations at the same instant must have "
                    "the same status."
                )

            previous = current

    @staticmethod
    def _build_periods(
        observations: tuple[Observation, ...],
        *,
        until: datetime | None,
    ) -> tuple[StatePeriod, ...]:
        """Transform ordered observations into state periods."""

        periods: list[StatePeriod] = []

        current_status = observations[0].status
        current_started_at = observations[0].observed_at

        for observation in observations[1:]:
            if observation.status is current_status:
                continue

            periods.append(
                StatePeriod(
                    status=current_status,
                    started_at=current_started_at,
                    ended_at=observation.observed_at,
                )
            )

            current_status = observation.status
            current_started_at = observation.observed_at

        periods.append(
            StatePeriod(
                status=current_status,
                started_at=current_started_at,
                ended_at=until,
            )
        )

        return tuple(periods)