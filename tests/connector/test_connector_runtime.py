"""Tests for ConnectorRuntime."""

from ohana_vision.connector import (
    ConnectorRuntime,
    ConnectorState,
    ConnectorStatistics,
)


def test_connector_runtime_starts_created() -> None:
    runtime = ConnectorRuntime()

    assert runtime.state is ConnectorState.CREATED
    assert runtime.is_ready is False
    assert runtime.is_running is False
    assert runtime.has_error is False


def test_connector_runtime_creates_statistics() -> None:
    runtime = ConnectorRuntime()

    assert isinstance(runtime.statistics, ConnectorStatistics)


def test_connector_runtime_uses_independent_statistics() -> None:
    first_runtime = ConnectorRuntime()
    second_runtime = ConnectorRuntime()

    assert first_runtime.statistics is not second_runtime.statistics


def test_connector_runtime_accepts_injected_statistics() -> None:
    statistics = ConnectorStatistics()

    runtime = ConnectorRuntime(statistics=statistics)

    assert runtime.statistics is statistics


def test_connector_runtime_can_be_marked_ready() -> None:
    runtime = ConnectorRuntime()

    runtime.mark_ready()

    assert runtime.state is ConnectorState.READY
    assert runtime.is_ready is True
    assert runtime.is_running is False
    assert runtime.has_error is False


def test_connector_runtime_can_be_marked_running() -> None:
    runtime = ConnectorRuntime()

    runtime.mark_running()

    assert runtime.state is ConnectorState.RUNNING
    assert runtime.is_ready is False
    assert runtime.is_running is True
    assert runtime.has_error is False


def test_connector_runtime_can_be_marked_in_error() -> None:
    runtime = ConnectorRuntime()

    runtime.mark_error()

    assert runtime.state is ConnectorState.ERROR
    assert runtime.is_ready is False
    assert runtime.is_running is False
    assert runtime.has_error is True


def test_connector_runtime_accepts_initial_state() -> None:
    runtime = ConnectorRuntime(state=ConnectorState.READY)

    assert runtime.state is ConnectorState.READY
    assert runtime.is_ready is True


def test_connector_runtime_can_recover_from_error() -> None:
    runtime = ConnectorRuntime(state=ConnectorState.ERROR)

    runtime.mark_ready()

    assert runtime.state is ConnectorState.READY
    assert runtime.has_error is False
