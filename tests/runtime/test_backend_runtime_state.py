"""Tests for backend runtime states."""

from ohana_vision.runtime import BackendRuntimeState


def test_backend_runtime_state_values() -> None:
    assert BackendRuntimeState.CREATED == "created"
    assert BackendRuntimeState.STARTING == "starting"
    assert BackendRuntimeState.RUNNING == "running"
    assert BackendRuntimeState.STOPPING == "stopping"
    assert BackendRuntimeState.STOPPED == "stopped"
    assert BackendRuntimeState.FAILED == "failed"


def test_starting_state_is_active() -> None:
    assert BackendRuntimeState.STARTING.active is True


def test_running_state_is_active() -> None:
    assert BackendRuntimeState.RUNNING.active is True


def test_stopping_state_is_active() -> None:
    assert BackendRuntimeState.STOPPING.active is True


def test_created_state_is_not_active() -> None:
    assert BackendRuntimeState.CREATED.active is False


def test_stopped_state_is_terminal() -> None:
    assert BackendRuntimeState.STOPPED.terminal is True


def test_failed_state_is_terminal() -> None:
    assert BackendRuntimeState.FAILED.terminal is True


def test_running_state_is_not_terminal() -> None:
    assert BackendRuntimeState.RUNNING.terminal is False


def test_running_state_is_healthy() -> None:
    assert BackendRuntimeState.RUNNING.healthy is True


def test_non_running_states_are_not_healthy() -> None:
    states = (
        BackendRuntimeState.CREATED,
        BackendRuntimeState.STARTING,
        BackendRuntimeState.STOPPING,
        BackendRuntimeState.STOPPED,
        BackendRuntimeState.FAILED,
    )

    assert all(state.healthy is False for state in states)
