"""Health engine evaluating projected infrastructure state."""

from collections import defaultdict
from collections.abc import Iterable
from datetime import UTC, datetime

from ohanna_vision.domain.capability_state import CapabilityState
from ohanna_vision.domain.criticality import Criticality
from ohanna_vision.domain.health import HealthStatus
from ohanna_vision.domain.infrastructure_state import InfrastructureState
from ohanna_vision.health.health_policy import CapabilityHealthPolicy
from ohanna_vision.health.health_report import (
    HealthAssessment,
    HealthEntityType,
    HealthReport,
)

type CapabilityKey = tuple[str, str, str]


_STATUS_PRIORITY: dict[HealthStatus, int] = {
    HealthStatus.HEALTHY: 0,
    HealthStatus.UNKNOWN: 1,
    HealthStatus.STALE: 2,
    HealthStatus.DEGRADED: 3,
    HealthStatus.UNAVAILABLE: 4,
}

_CRITICALITY_PRIORITY: dict[Criticality, int] = {
    Criticality.LOW: 0,
    Criticality.NORMAL: 1,
    Criticality.HIGH: 2,
    Criticality.CRITICAL: 3,
}


class DuplicateHealthPolicyError(ValueError):
    """Raised when several policies target the same capability."""


class HealthEngine:
    """Evaluate the health of a projected infrastructure state."""

    def __init__(
        self,
        policies: Iterable[CapabilityHealthPolicy] = (),
    ) -> None:
        """Initialize the engine with capability policies."""

        self._policies: dict[
            CapabilityKey,
            CapabilityHealthPolicy,
        ] = {}

        for policy in policies:
            if policy.key in self._policies:
                raise DuplicateHealthPolicyError(
                    f"A health policy already exists for {'/'.join(policy.key)}."
                )

            self._policies[policy.key] = policy

    def evaluate(
        self,
        infrastructure: InfrastructureState,
        *,
        now: datetime | None = None,
    ) -> HealthReport:
        """Evaluate all infrastructure health levels."""

        evaluated_at = now or datetime.now(UTC)

        if evaluated_at.tzinfo is None:
            raise ValueError("now must be timezone-aware.")

        capability_assessments = tuple(
            self._evaluate_capability(
                capability,
                evaluated_at=evaluated_at,
            )
            for node in infrastructure.nodes
            for service in node.services
            for capability in service.capabilities
        )

        service_assessments = self._evaluate_services(capability_assessments)
        node_assessments = self._evaluate_nodes(service_assessments)
        infrastructure_assessment = self._evaluate_infrastructure(node_assessments)

        return HealthReport(
            evaluated_at=evaluated_at,
            capabilities=capability_assessments,
            services=service_assessments,
            nodes=node_assessments,
            infrastructure=infrastructure_assessment,
        )

    def _evaluate_capability(
        self,
        capability: CapabilityState,
        *,
        evaluated_at: datetime,
    ) -> HealthAssessment:
        """Evaluate one capability state."""

        key = (
            capability.node_id,
            capability.service_id,
            capability.capability_id,
        )
        policy = self._policies.get(key)

        criticality = policy.criticality if policy is not None else Criticality.NORMAL

        status = capability.health.status
        reason = capability.health.reason or capability.message

        if (
            policy is not None
            and policy.stale_after is not None
            and evaluated_at - capability.observed_at > policy.stale_after
        ):
            status = HealthStatus.STALE
            reason = (
                "The latest observation is older than the configured "
                f"limit of {policy.stale_after}."
            )

        return HealthAssessment(
            entity_type=HealthEntityType.CAPABILITY,
            entity_id=(
                f"{capability.node_id}/"
                f"{capability.service_id}/"
                f"{capability.capability_id}"
            ),
            status=status,
            criticality=criticality,
            reason=reason,
            observed_at=capability.observed_at,
        )

    def _evaluate_services(
        self,
        capabilities: tuple[HealthAssessment, ...],
    ) -> tuple[HealthAssessment, ...]:
        """Aggregate capability assessments by service."""

        grouped: dict[str, list[HealthAssessment]] = defaultdict(list)

        for capability in capabilities:
            node_id, service_id, _ = capability.entity_id.split("/", 2)
            grouped[f"{node_id}/{service_id}"].append(capability)

        return tuple(
            self._aggregate(
                entity_type=HealthEntityType.SERVICE,
                entity_id=entity_id,
                children=grouped[entity_id],
            )
            for entity_id in sorted(grouped)
        )

    def _evaluate_nodes(
        self,
        services: tuple[HealthAssessment, ...],
    ) -> tuple[HealthAssessment, ...]:
        """Aggregate service assessments by node."""

        grouped: dict[str, list[HealthAssessment]] = defaultdict(list)

        for service in services:
            node_id, _ = service.entity_id.split("/", 1)
            grouped[node_id].append(service)

        return tuple(
            self._aggregate(
                entity_type=HealthEntityType.NODE,
                entity_id=node_id,
                children=grouped[node_id],
            )
            for node_id in sorted(grouped)
        )

    def _evaluate_infrastructure(
        self,
        nodes: tuple[HealthAssessment, ...],
    ) -> HealthAssessment:
        """Aggregate node assessments into global health."""

        if not nodes:
            return HealthAssessment(
                entity_type=HealthEntityType.INFRASTRUCTURE,
                entity_id="infrastructure",
                status=HealthStatus.UNKNOWN,
                criticality=Criticality.NORMAL,
                reason="No infrastructure health information is available.",
            )

        return self._aggregate(
            entity_type=HealthEntityType.INFRASTRUCTURE,
            entity_id="infrastructure",
            children=nodes,
        )

    def _aggregate(
        self,
        *,
        entity_type: HealthEntityType,
        entity_id: str,
        children: Iterable[HealthAssessment],
    ) -> HealthAssessment:
        """Aggregate child health according to criticality rules."""

        values = tuple(children)

        if not values:
            return HealthAssessment(
                entity_type=entity_type,
                entity_id=entity_id,
                status=HealthStatus.UNKNOWN,
                criticality=Criticality.NORMAL,
                reason="No child health information is available.",
            )

        impacts = tuple(
            (
                self._parent_impact(child),
                child,
            )
            for child in values
        )

        status, source = max(
            impacts,
            key=lambda item: _STATUS_PRIORITY[item[0]],
        )

        criticality = max(
            (child.criticality for child in values),
            key=lambda value: _CRITICALITY_PRIORITY[value],
        )

        reason = None

        if status is not HealthStatus.HEALTHY:
            reason = (
                f"Health inherited from {source.entity_type.value} "
                f"{source.entity_id}: {source.status.value}."
            )

        return HealthAssessment(
            entity_type=entity_type,
            entity_id=entity_id,
            status=status,
            criticality=criticality,
            reason=reason,
            observed_at=self._latest_observation_date(values),
        )

    @staticmethod
    def _parent_impact(
        assessment: HealthAssessment,
    ) -> HealthStatus:
        """Return the impact of one assessment on its parent."""

        if assessment.status is HealthStatus.HEALTHY:
            return HealthStatus.HEALTHY

        if assessment.status is HealthStatus.DEGRADED:
            return HealthStatus.DEGRADED

        if assessment.status is HealthStatus.UNAVAILABLE:
            if assessment.criticality is Criticality.CRITICAL:
                return HealthStatus.UNAVAILABLE

            return HealthStatus.DEGRADED

        if assessment.status in {
            HealthStatus.STALE,
            HealthStatus.UNKNOWN,
        }:
            if assessment.criticality in {
                Criticality.HIGH,
                Criticality.CRITICAL,
            }:
                return HealthStatus.DEGRADED

            return assessment.status

        return assessment.status

    @staticmethod
    def _latest_observation_date(
        assessments: Iterable[HealthAssessment],
    ) -> datetime | None:
        """Return the latest child observation date."""

        dates = tuple(
            assessment.observed_at
            for assessment in assessments
            if assessment.observed_at is not None
        )

        if not dates:
            return None

        return max(dates)
