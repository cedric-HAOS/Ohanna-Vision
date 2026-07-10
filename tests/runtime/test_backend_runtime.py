"""Tests for the Ohanna-Vision backend runtime."""

from datetime import UTC, datetime

import pytest

from ohanna_vision.runtime import (
    BackendRuntime,
    BackendRuntimeError,
    BackendRuntimeState,
    RuntimeStatistics,
)

STARTED_AT = datetime(
    2026,
    7,
    10,
    15,
    0,
    tzinfo=UTC,
)

STOPPED_AT = datetime(
    2026,
    7,
    10,
    16,
    0,
    tzinfo=UTC,
)


def test_backend_runtime_is_created_by_default() -> None:
    runtime = BackendRuntime()

    assert runtime.state is BackendRuntimeState.CREATED
    assert runtime.running is False
    assert runtime.healthy is False
    assert runtime.started_at is None
    assert runtime.stopped_at is None
    assert runtime.statistics == RuntimeStatistics()


def test_start_marks_runtime_as_running() -> None:
    runtime = BackendRuntime(clock=lambda: STARTED_AT)

    runtime.start()

    assert runtime.state is BackendRuntimeState.RUNNING
    assert runtime.running is True
    assert runtime.healthy is True
    assert runtime.started_at == STARTED_AT
    assert runtime.stopped_at is None


def test_stop_marks_runtime_as_stopped() -> None:
    instants = iter((STARTED_AT, STOPPED_AT))
    runtime = BackendRuntime(clock=lambda: next(instants))

    runtime.start()
    runtime.stop()

    assert runtime.state is BackendRuntimeState.STOPPED
    assert runtime.running is False
    assert runtime.healthy is False
    assert runtime.started_at == STARTED_AT
    assert runtime.stopped_at == STOPPED_AT


def test_stopped_runtime_can_be_started_again() -> None:
    restarted_at = datetime(
        2026,
        7,
        10,
        17,
        0,
        tzinfo=UTC,
    )
    instants = iter((STARTED_AT, STOPPED_AT, restarted_at))
    runtime = BackendRuntime(clock=lambda: next(instants))

    runtime.start()
    runtime.stop()
    runtime.start()

    assert runtime.state is BackendRuntimeState.RUNNING
    assert runtime.started_at == restarted_at
    assert runtime.stopped_at is None


def test_start_rejects_running_runtime() -> None:
    runtime = BackendRuntime(clock=lambda: STARTED_AT)
    runtime.start()

    with pytest.raises(
        BackendRuntimeError,
        match="Cannot start backend runtime from state running",
    ):
        runtime.start()


def test_start_rejects_failed_runtime() -> None:
    runtime = BackendRuntime(clock=lambda: STARTED_AT)
    runtime.fail(STARTED_AT)

    with pytest.raises(
        BackendRuntimeError,
        match="Cannot start backend runtime from state failed",
    ):
        runtime.start()


def test_stop_rejects_created_runtime() -> None:
    runtime = BackendRuntime()

    with pytest.raises(
        BackendRuntimeError,
        match="Cannot stop backend runtime from state created",
    ):
        runtime.stop()


def test_stop_rejects_already_stopped_runtime() -> None:
    instants = iter((STARTED_AT, STOPPED_AT))
    runtime = BackendRuntime(clock=lambda: next(instants))
    runtime.start()
    runtime.stop()

    with pytest.raises(
        BackendRuntimeError,
        match="Cannot stop backend runtime from state stopped",
    ):
        runtime.stop()


def test_fail_marks_runtime_as_failed() -> None:
    runtime = BackendRuntime()

    runtime.fail(STARTED_AT)

    assert runtime.state is BackendRuntimeState.FAILED
    assert runtime.running is False
    assert runtime.healthy is False
    assert runtime.statistics.errors == 1
    assert runtime.statistics.last_error_at == STARTED_AT


def test_reset_statistics_restores_empty_statistics() -> None:
    runtime = BackendRuntime()
    runtime.fail(STARTED_AT)

    runtime.reset_statistics()

    assert runtime.statistics == RuntimeStatistics()
    assert runtime.state is BackendRuntimeState.FAILED


def test_snapshot_contains_runtime_state_and_statistics() -> None:
    runtime = BackendRuntime(clock=lambda: STARTED_AT)
    runtime.start()

    snapshot = runtime.snapshot(
        observations_stored=12,
        service_timelines=4,
        node_timelines=2,
        infrastructure_timelines=1,
    )

    assert snapshot.state is BackendRuntimeState.RUNNING
    assert snapshot.statistics is runtime.statistics
    assert snapshot.generated_at == STARTED_AT
    assert snapshot.observations_stored == 12
    assert snapshot.service_timelines == 4
    assert snapshot.node_timelines == 2
    assert snapshot.infrastructure_timelines == 1
    assert snapshot.timeline_count == 7


def test_snapshot_uses_zero_counters_by_default() -> None:
    runtime = BackendRuntime(clock=lambda: STARTED_AT)

    snapshot = runtime.snapshot()

    assert snapshot.observations_stored == 0
    assert snapshot.timeline_count == 0


def test_start_rejects_naive_clock_datetime() -> None:
    naive_datetime = datetime(2026, 7, 10, 15, 0)
    runtime = BackendRuntime(clock=lambda: naive_datetime)

    with pytest.raises(
        ValueError,
        match="Runtime datetimes must be timezone-aware",
    ):
        runtime.start()

    assert runtime.state is BackendRuntimeState.FAILED


def test_stop_rejects_naive_clock_datetime() -> None:
    naive_datetime = datetime(2026, 7, 10, 16, 0)
    instants = iter((STARTED_AT, naive_datetime))
    runtime = BackendRuntime(clock=lambda: next(instants))
    runtime.start()

    with pytest.raises(
        ValueError,
        match="Runtime datetimes must be timezone-aware",
    ):
        runtime.stop()

    assert runtime.state is BackendRuntimeState.FAILED


def test_snapshot_rejects_naive_clock_datetime() -> None:
    naive_datetime = datetime(2026, 7, 10, 15, 0)
    runtime = BackendRuntime(clock=lambda: naive_datetime)

    with pytest.raises(
        ValueError,
        match="Runtime datetimes must be timezone-aware",
    ):
        runtime.snapshot()

def test_record_received_updates_runtime_statistics() -> None:
    runtime = BackendRuntime()

    runtime.record_received(STARTED_AT)

    assert runtime.statistics.observations_received == 1
    assert runtime.statistics.last_observation_at == STARTED_AT


def test_record_accepted_updates_runtime_statistics() -> None:
    runtime = BackendRuntime()

    runtime.record_received(STARTED_AT)
    runtime.record_accepted()

    assert runtime.statistics.observations_accepted == 1


def test_record_rejected_updates_runtime_statistics() -> None:
    runtime = BackendRuntime()

    runtime.record_received(STARTED_AT)
    runtime.record_rejected()

    assert runtime.statistics.observations_rejected == 1


def test_record_error_updates_runtime_statistics() -> None:
    runtime = BackendRuntime()

    runtime.record_error(STARTED_AT)

    assert runtime.statistics.errors == 1
    assert runtime.statistics.last_error_at == STARTED_AT


def test_fail_uses_runtime_record_error() -> None:
    runtime = BackendRuntime()

    runtime.fail(STARTED_AT)

    assert runtime.state is BackendRuntimeState.FAILED
    assert runtime.statistics.errors == 1