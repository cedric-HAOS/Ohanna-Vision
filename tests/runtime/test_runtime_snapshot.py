"""Tests for backend runtime snapshots."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime

import pytest

from ohanna_vision.runtime import (
    BackendRuntimeState,
    RuntimeSnapshot,
    RuntimeStatistics,
)


def make_snapshot(
    *,
    state: BackendRuntimeState = BackendRuntimeState.RUNNING,
    observations_stored: int = 0,
    service_timelines: int = 0,
    node_timelines: int = 0,
    infrastructure_timelines: int = 0,
) -> RuntimeSnapshot:
    """Create a runtime snapshot for tests."""

    return RuntimeSnapshot(
        state=state,
        statistics=RuntimeStatistics(),
        generated_at=datetime(
            2026,
            7,
            10,
            15,
            0,
            tzinfo=UTC,
        ),
        observations_stored=observations_stored,
        service_timelines=service_timelines,
        node_timelines=node_timelines,
        infrastructure_timelines=infrastructure_timelines,
    )


def test_runtime_snapshot_stores_runtime_information() -> None:
    statistics = RuntimeStatistics()
    generated_at = datetime(
        2026,
        7,
        10,
        15,
        0,
        tzinfo=UTC,
    )

    snapshot = RuntimeSnapshot(
        state=BackendRuntimeState.RUNNING,
        statistics=statistics,
        generated_at=generated_at,
        observations_stored=12,
        service_timelines=4,
        node_timelines=2,
        infrastructure_timelines=1,
    )

    assert snapshot.state is BackendRuntimeState.RUNNING
    assert snapshot.statistics is statistics
    assert snapshot.generated_at == generated_at
    assert snapshot.observations_stored == 12
    assert snapshot.service_timelines == 4
    assert snapshot.node_timelines == 2
    assert snapshot.infrastructure_timelines == 1


def test_runtime_snapshot_has_zero_counters_by_default() -> None:
    snapshot = make_snapshot()

    assert snapshot.observations_stored == 0
    assert snapshot.service_timelines == 0
    assert snapshot.node_timelines == 0
    assert snapshot.infrastructure_timelines == 0


def test_running_is_true_when_runtime_is_running() -> None:
    snapshot = make_snapshot(
        state=BackendRuntimeState.RUNNING,
    )

    assert snapshot.running is True


def test_running_is_false_when_runtime_is_not_running() -> None:
    snapshot = make_snapshot(
        state=BackendRuntimeState.STOPPED,
    )

    assert snapshot.running is False


def test_healthy_uses_runtime_state_health() -> None:
    running = make_snapshot(
        state=BackendRuntimeState.RUNNING,
    )
    failed = make_snapshot(
        state=BackendRuntimeState.FAILED,
    )

    assert running.healthy is True
    assert failed.healthy is False


def test_timeline_count_combines_all_timeline_levels() -> None:
    snapshot = make_snapshot(
        service_timelines=4,
        node_timelines=2,
        infrastructure_timelines=1,
    )

    assert snapshot.timeline_count == 7


def test_has_observations_is_true_when_observations_are_stored() -> None:
    snapshot = make_snapshot(observations_stored=1)

    assert snapshot.has_observations is True


def test_has_observations_is_false_when_store_is_empty() -> None:
    snapshot = make_snapshot(observations_stored=0)

    assert snapshot.has_observations is False


@pytest.mark.parametrize(
    ("field_name", "field_value"),
    [
        ("observations_stored", -1),
        ("service_timelines", -1),
        ("node_timelines", -1),
        ("infrastructure_timelines", -1),
    ],
)
def test_runtime_snapshot_rejects_negative_counters(
    field_name: str,
    field_value: int,
) -> None:
    arguments = {
        "state": BackendRuntimeState.RUNNING,
        "statistics": RuntimeStatistics(),
        "generated_at": datetime(
            2026,
            7,
            10,
            15,
            0,
            tzinfo=UTC,
        ),
        field_name: field_value,
    }

    with pytest.raises(
        ValueError,
        match=f"{field_name} cannot be negative",
    ):
        RuntimeSnapshot(**arguments)


def test_runtime_snapshot_is_immutable() -> None:
    snapshot = make_snapshot()

    with pytest.raises(FrozenInstanceError):
        snapshot.observations_stored = 1  # type: ignore[misc]
