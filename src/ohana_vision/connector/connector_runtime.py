"""Runtime state for an observation connector."""

from dataclasses import dataclass, field

from ohana_vision.connector.connector_state import ConnectorState
from ohana_vision.connector.connector_statistics import ConnectorStatistics


@dataclass(slots=True)
class ConnectorRuntime:
    """Represent the operational runtime of a connector."""

    state: ConnectorState = ConnectorState.CREATED
    statistics: ConnectorStatistics = field(default_factory=ConnectorStatistics)

    @property
    def is_ready(self) -> bool:
        """Return whether the connector is ready to receive observations."""
        return self.state is ConnectorState.READY

    @property
    def is_running(self) -> bool:
        """Return whether the connector is currently processing observations."""
        return self.state is ConnectorState.RUNNING

    @property
    def has_error(self) -> bool:
        """Return whether the connector is in an error state."""
        return self.state is ConnectorState.ERROR

    def mark_ready(self) -> None:
        """Mark the connector as ready."""
        self.state = ConnectorState.READY

    def mark_running(self) -> None:
        """Mark the connector as running."""
        self.state = ConnectorState.RUNNING

    def mark_error(self) -> None:
        """Mark the connector as being in error."""
        self.state = ConnectorState.ERROR
