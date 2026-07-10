"""Observation model received from Ohanna-Agent."""

from collections.abc import Mapping
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from ohanna_vision.domain.health import HealthStatus


@dataclass(frozen=True, slots=True)
class Observation:
    """Represent an immutable fact observed by Ohanna-Agent."""

    capability_id: str
    service_id: str
    node_id: str
    status: HealthStatus
    observed_at: datetime
    observation_id: UUID = field(default_factory=uuid4)
    message: str | None = None
    latency_ms: float | None = None
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate observation invariants."""

        if not self.capability_id.strip():
            raise ValueError("capability_id must not be empty.")

        if not self.service_id.strip():
            raise ValueError("service_id must not be empty.")

        if not self.node_id.strip():
            raise ValueError("node_id must not be empty.")

        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware.")

        if self.latency_ms is not None and self.latency_ms < 0:
            raise ValueError("latency_ms must not be negative.")