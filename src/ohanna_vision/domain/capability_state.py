"""Current state of an infrastructure capability."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from ohanna_vision.domain.health import Health


@dataclass(frozen=True, slots=True)
class CapabilityState:
    """Represent the latest known state of a capability."""

    capability_id: str
    service_id: str
    node_id: str
    health: Health
    observed_at: datetime
    state_since: datetime
    message: str | None = None
    latency_ms: float | None = None
    metadata: Mapping[str, Any] | None = None

    def __post_init__(self) -> None:
        """Validate capability state invariants."""

        if not self.capability_id.strip():
            raise ValueError("capability_id must not be empty.")

        if not self.service_id.strip():
            raise ValueError("service_id must not be empty.")

        if not self.node_id.strip():
            raise ValueError("node_id must not be empty.")

        if self.observed_at.tzinfo is None:
            raise ValueError("observed_at must be timezone-aware.")

        if self.state_since.tzinfo is None:
            raise ValueError("state_since must be timezone-aware.")

        if self.state_since > self.observed_at:
            raise ValueError("state_since must not be after observed_at.")

        if self.latency_ms is not None and self.latency_ms < 0:
            raise ValueError("latency_ms must not be negative.")

    @property
    def age_seconds(self) -> float:
        """Return the age of the latest observation in seconds."""

        return max(
            0.0,
            (datetime.now(UTC) - self.observed_at).total_seconds(),
        )

    @property
    def duration_seconds(self) -> float:
        """Return how long the capability has remained in this state."""

        return max(
            0.0,
            (self.observed_at - self.state_since).total_seconds(),
        )
