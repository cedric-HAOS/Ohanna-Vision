"""Runtime statistics for an observation connector."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class ConnectorStatistics:
    """Track observation reception statistics for a connector."""

    received_count: int = 0
    failed_count: int = 0
    last_received_at: datetime | None = None

    @property
    def successful_count(self) -> int:
        """Return the number of successfully received observations."""
        return self.received_count - self.failed_count

    def record_success(self, received_at: datetime) -> None:
        """Record a successfully received observation."""
        self.received_count += 1
        self.last_received_at = received_at

    def record_failure(self, received_at: datetime) -> None:
        """Record a failed observation reception."""
        self.received_count += 1
        self.failed_count += 1
        self.last_received_at = received_at

    def reset(self) -> None:
        """Reset all connector statistics."""
        self.received_count = 0
        self.failed_count = 0
        self.last_received_at = None