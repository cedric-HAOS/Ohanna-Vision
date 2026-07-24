"""Connector receiving observations from Ohana-Agent."""

from collections.abc import Callable
from datetime import UTC, datetime

from ohana_vision.connector.connector_result import ConnectorResult
from ohana_vision.connector.connector_runtime import ConnectorRuntime
from ohana_vision.connector.observation_processor_protocol import (
    ObservationProcessorProtocol,
)
from ohana_vision.domain import Observation

Timer = Callable[[], datetime]


class AgentConnector:
    """Receive agent observations and forward them to the processor."""

    def __init__(
        self,
        processor: ObservationProcessorProtocol,
        runtime: ConnectorRuntime | None = None,
        timer: Timer | None = None,
    ) -> None:
        """Initialize the connector and its dependencies."""
        self._processor = processor
        self._runtime = runtime or ConnectorRuntime()
        self._timer = timer or self._utc_now

    @property
    def runtime(self) -> ConnectorRuntime:
        """Return the connector runtime."""
        return self._runtime

    def initialize(self) -> None:
        """Prepare the connector to receive observations."""
        self._runtime.mark_ready()

    def receive(self, observation: Observation) -> ConnectorResult:
        """Receive and process an observation."""
        received_at = self._timer()
        self._runtime.mark_running()

        try:
            self._processor.process(observation)
        except Exception as error:
            self._runtime.statistics.record_failure(received_at)
            self._runtime.mark_error()

            return ConnectorResult.failed(f"Observation processing failed: {error}")

        self._runtime.statistics.record_success(received_at)
        self._runtime.mark_ready()

        return ConnectorResult.succeeded()

    @staticmethod
    def _utc_now() -> datetime:
        """Return the current UTC instant."""
        return datetime.now(UTC)
