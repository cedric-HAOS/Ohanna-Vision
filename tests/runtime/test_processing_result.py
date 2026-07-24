"""Tests for observation processing results."""

from dataclasses import FrozenInstanceError
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from ohana_vision.runtime import (
    BackendRuntimeState,
    ProcessingResult,
    RuntimeSnapshot,
    RuntimeStatistics,
)

OBSERVATION_ID = UUID("00000000-0000-0000-0000-000000000001")

GENERATED_AT = datetime(
    2026,
    7,
    10,
    15,
    0,
    tzinfo=UTC,
)


def make_snapshot() -> RuntimeSnapshot:
    """Create a deterministic runtime snapshot."""

    return RuntimeSnapshot(
        state=BackendRuntimeState.RUNNING,
        statistics=RuntimeStatistics(),
        generated_at=GENERATED_AT,
        observations_stored=1,
        service_timelines=1,
    )


def test_processing_result_stores_accepted_result() -> None:
    snapshot = make_snapshot()
    duration = timedelta(milliseconds=12)

    result = ProcessingResult(
        observation_id=OBSERVATION_ID,
        accepted=True,
        snapshot=snapshot,
        duration=duration,
        timeline_updated=True,
    )

    assert result.observation_id == OBSERVATION_ID
    assert result.accepted is True
    assert result.rejected is False
    assert result.snapshot is snapshot
    assert result.duration == duration
    assert result.timeline_updated is True
    assert result.reason is None


def test_accepted_result_factory_creates_successful_result() -> None:
    snapshot = make_snapshot()

    result = ProcessingResult.accepted_result(
        observation_id=OBSERVATION_ID,
        snapshot=snapshot,
        duration=timedelta(milliseconds=8),
        timeline_updated=True,
    )

    assert result.accepted is True
    assert result.rejected is False
    assert result.timeline_updated is True
    assert result.reason is None


def test_rejected_result_factory_creates_rejected_result() -> None:
    snapshot = make_snapshot()

    result = ProcessingResult.rejected_result(
        observation_id=OBSERVATION_ID,
        snapshot=snapshot,
        duration=timedelta(milliseconds=3),
        reason="Observation already processed",
    )

    assert result.accepted is False
    assert result.rejected is True
    assert result.timeline_updated is False
    assert result.reason == "Observation already processed"


def test_duration_ms_returns_duration_in_milliseconds() -> None:
    result = ProcessingResult.accepted_result(
        observation_id=OBSERVATION_ID,
        snapshot=make_snapshot(),
        duration=timedelta(milliseconds=12.5),
        timeline_updated=False,
    )

    assert result.duration_ms == pytest.approx(12.5)


def test_zero_duration_is_allowed() -> None:
    result = ProcessingResult.accepted_result(
        observation_id=OBSERVATION_ID,
        snapshot=make_snapshot(),
        duration=timedelta(),
        timeline_updated=False,
    )

    assert result.duration == timedelta()
    assert result.duration_ms == 0.0


def test_negative_duration_is_rejected() -> None:
    with pytest.raises(
        ValueError,
        match="duration cannot be negative",
    ):
        ProcessingResult.accepted_result(
            observation_id=OBSERVATION_ID,
            snapshot=make_snapshot(),
            duration=timedelta(milliseconds=-1),
            timeline_updated=False,
        )


def test_accepted_result_rejects_reason() -> None:
    with pytest.raises(
        ValueError,
        match=("An accepted processing result cannot have a rejection reason"),
    ):
        ProcessingResult(
            observation_id=OBSERVATION_ID,
            accepted=True,
            snapshot=make_snapshot(),
            duration=timedelta(milliseconds=1),
            reason="Unexpected reason",
        )


@pytest.mark.parametrize(
    "reason",
    [
        None,
        "",
    ],
)
def test_rejected_result_requires_reason(
    reason: str | None,
) -> None:
    with pytest.raises(
        ValueError,
        match="A rejected processing result must have a reason",
    ):
        ProcessingResult(
            observation_id=OBSERVATION_ID,
            accepted=False,
            snapshot=make_snapshot(),
            duration=timedelta(milliseconds=1),
            reason=reason,
        )


def test_rejected_result_cannot_update_timeline() -> None:
    with pytest.raises(
        ValueError,
        match="A rejected observation cannot update a timeline",
    ):
        ProcessingResult(
            observation_id=OBSERVATION_ID,
            accepted=False,
            snapshot=make_snapshot(),
            duration=timedelta(milliseconds=1),
            timeline_updated=True,
            reason="Invalid observation",
        )


def test_processing_result_is_immutable() -> None:
    result = ProcessingResult.accepted_result(
        observation_id=OBSERVATION_ID,
        snapshot=make_snapshot(),
        duration=timedelta(milliseconds=1),
        timeline_updated=True,
    )

    with pytest.raises(FrozenInstanceError):
        result.accepted = False  # type: ignore[misc]
