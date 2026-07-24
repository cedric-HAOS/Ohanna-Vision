"""Tests for AgentConnector."""

from datetime import UTC, datetime

import pytest

from ohana_vision.connector import (
    AgentConnector,
    ConnectorRuntime,
    ConnectorState,
)
from ohana_vision.domain import HealthStatus, Observation


class FakeObservationProcessor:
    """Test processor recording received observations."""

    def __init__(self) -> None:
        self.observations: list[Observation] = []

    def process(self, observation: Observation) -> object:
        """Record an observation."""
        self.observations.append(observation)
        return object()


class FailingObservationProcessor:
    """Test processor raising an error."""

    def process(self, observation: Observation) -> object:
        """Raise a processing error."""
        raise RuntimeError("processor unavailable")


def make_instant() -> datetime:
    """Return a stable timezone-aware instant."""
    return datetime(2026, 7, 11, 14, 0, tzinfo=UTC)


def make_observation() -> Observation:
    """Create an observation for connector tests."""
    return Observation(
        capability_id="dns-resolution",
        service_id="dns-primary",
        node_id="infra-01",
        status=HealthStatus.HEALTHY,
        observed_at=make_instant(),
        latency_ms=4.2,
        metadata={},
    )


def test_agent_connector_starts_with_created_runtime() -> None:
    connector = AgentConnector(processor=FakeObservationProcessor())

    assert connector.runtime.state is ConnectorState.CREATED


def test_agent_connector_uses_injected_runtime() -> None:
    runtime = ConnectorRuntime()

    connector = AgentConnector(
        processor=FakeObservationProcessor(),
        runtime=runtime,
    )

    assert connector.runtime is runtime


def test_agent_connector_initializes_runtime() -> None:
    connector = AgentConnector(processor=FakeObservationProcessor())

    connector.initialize()

    assert connector.runtime.state is ConnectorState.READY
    assert connector.runtime.is_ready is True


def test_agent_connector_forwards_observation_to_processor() -> None:
    processor = FakeObservationProcessor()
    connector = AgentConnector(processor=processor)
    observation = make_observation()

    connector.receive(observation)

    assert processor.observations == [observation]


def test_agent_connector_returns_success_result() -> None:
    connector = AgentConnector(processor=FakeObservationProcessor())

    result = connector.receive(make_observation())

    assert result.success is True
    assert result.message == "Observation received successfully."


def test_agent_connector_records_success() -> None:
    received_at = make_instant()
    connector = AgentConnector(
        processor=FakeObservationProcessor(),
        timer=lambda: received_at,
    )

    connector.receive(make_observation())

    statistics = connector.runtime.statistics
    assert statistics.received_count == 1
    assert statistics.failed_count == 0
    assert statistics.successful_count == 1
    assert statistics.last_received_at is received_at


def test_agent_connector_returns_to_ready_after_success() -> None:
    connector = AgentConnector(processor=FakeObservationProcessor())

    connector.receive(make_observation())

    assert connector.runtime.state is ConnectorState.READY
    assert connector.runtime.is_ready is True


def test_agent_connector_returns_failure_result() -> None:
    connector = AgentConnector(
        processor=FailingObservationProcessor(),
    )

    result = connector.receive(make_observation())

    assert result.success is False
    assert result.message == ("Observation processing failed: processor unavailable")


def test_agent_connector_records_failure() -> None:
    received_at = make_instant()
    connector = AgentConnector(
        processor=FailingObservationProcessor(),
        timer=lambda: received_at,
    )

    connector.receive(make_observation())

    statistics = connector.runtime.statistics
    assert statistics.received_count == 1
    assert statistics.failed_count == 1
    assert statistics.successful_count == 0
    assert statistics.last_received_at is received_at


def test_agent_connector_enters_error_state_after_failure() -> None:
    connector = AgentConnector(
        processor=FailingObservationProcessor(),
    )

    connector.receive(make_observation())

    assert connector.runtime.state is ConnectorState.ERROR
    assert connector.runtime.has_error is True


def test_agent_connector_can_be_reinitialized_after_failure() -> None:
    connector = AgentConnector(
        processor=FailingObservationProcessor(),
    )
    connector.receive(make_observation())

    connector.initialize()

    assert connector.runtime.state is ConnectorState.READY
    assert connector.runtime.has_error is False


def test_agent_connector_records_each_success() -> None:
    connector = AgentConnector(processor=FakeObservationProcessor())

    connector.receive(make_observation())
    connector.receive(make_observation())

    statistics = connector.runtime.statistics
    assert statistics.received_count == 2
    assert statistics.failed_count == 0
    assert statistics.successful_count == 2


def test_agent_connector_records_success_after_recovery() -> None:
    runtime = ConnectorRuntime()
    failing_connector = AgentConnector(
        processor=FailingObservationProcessor(),
        runtime=runtime,
    )

    failing_connector.receive(make_observation())
    failing_connector.initialize()

    successful_connector = AgentConnector(
        processor=FakeObservationProcessor(),
        runtime=runtime,
    )

    result = successful_connector.receive(make_observation())

    assert result.success is True
    assert runtime.state is ConnectorState.READY
    assert runtime.statistics.received_count == 2
    assert runtime.statistics.failed_count == 1
    assert runtime.statistics.successful_count == 1


def test_agent_connector_updates_last_received_at_for_each_reception() -> None:
    instants = iter(
        [
            datetime(2026, 7, 11, 14, 0, tzinfo=UTC),
            datetime(2026, 7, 11, 14, 5, tzinfo=UTC),
        ]
    )
    connector = AgentConnector(
        processor=FakeObservationProcessor(),
        timer=lambda: next(instants),
    )

    connector.receive(make_observation())
    connector.receive(make_observation())

    assert connector.runtime.statistics.last_received_at == datetime(
        2026,
        7,
        11,
        14,
        5,
        tzinfo=UTC,
    )


def test_agent_connector_does_not_catch_keyboard_interrupt() -> None:
    class InterruptingProcessor:
        def process(self, observation: Observation) -> object:
            raise KeyboardInterrupt

    connector = AgentConnector(processor=InterruptingProcessor())

    with pytest.raises(KeyboardInterrupt):
        connector.receive(make_observation())
