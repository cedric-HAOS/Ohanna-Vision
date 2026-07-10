"""Health assessment results."""

from dataclasses import dataclass
from datetime import datetime
from enum import StrEnum

from ohanna_vision.domain.criticality import Criticality
from ohanna_vision.domain.health import HealthStatus


class HealthEntityType(StrEnum):
    """Types of entities evaluated by the health engine."""

    CAPABILITY = "capability"
    SERVICE = "service"
    NODE = "node"
    INFRASTRUCTURE = "infrastructure"


@dataclass(frozen=True, slots=True)
class HealthAssessment:
    """Represent the evaluated health of one domain entity."""

    entity_type: HealthEntityType
    entity_id: str
    status: HealthStatus
    criticality: Criticality
    reason: str | None = None
    observed_at: datetime | None = None


@dataclass(frozen=True, slots=True)
class HealthReport:
    """Contain all health assessments for one evaluation."""

    evaluated_at: datetime
    capabilities: tuple[HealthAssessment, ...]
    services: tuple[HealthAssessment, ...]
    nodes: tuple[HealthAssessment, ...]
    infrastructure: HealthAssessment

    def capability(
        self,
        *,
        node_id: str,
        service_id: str,
        capability_id: str,
    ) -> HealthAssessment | None:
        """Return a capability assessment."""

        entity_id = f"{node_id}/{service_id}/{capability_id}"

        return next(
            (
                assessment
                for assessment in self.capabilities
                if assessment.entity_id == entity_id
            ),
            None,
        )

    def service(
        self,
        *,
        node_id: str,
        service_id: str,
    ) -> HealthAssessment | None:
        """Return a service assessment."""

        entity_id = f"{node_id}/{service_id}"

        return next(
            (
                assessment
                for assessment in self.services
                if assessment.entity_id == entity_id
            ),
            None,
        )

    def node(self, node_id: str) -> HealthAssessment | None:
        """Return a node assessment."""

        return next(
            (
                assessment
                for assessment in self.nodes
                if assessment.entity_id == node_id
            ),
            None,
        )