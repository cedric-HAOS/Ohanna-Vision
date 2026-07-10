"""Tests for backend runtime statistics."""

from datetime import UTC, datetime

import pytest

from ohanna_vision.runtime import RuntimeStatistics


def test_runtime_statistics_have_empty_defaults() -> None:
    statistics = RuntimeStatistics()

    assert statistics.observations_received == 0
    assert statistics.observations_accepted == 0
    assert statistics.observations_rejected == 0
    assert statistics.errors == 0
    assert statistics.last_observation_at is None
    assert statistics.last_error_at is None


def test_runtime_statistics_have_no_processed_observations_by_default() -> None:
    statistics = RuntimeStatistics()

    assert statistics.observations_processed == 0


def test_runtime_statistics_have_no_pending_observations_by_default() -> None:
    statistics = RuntimeStatistics()

    assert statistics.observations_pending == 0


def test_runtime_statistics_have_zero_acceptance_rate_by_default() -> None:
    statistics = RuntimeStatistics()

    assert statistics.acceptance_rate == 0.0


def test_record_received_returns_updated_statistics() -> None:
    received_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    statistics = RuntimeStatistics()

    updated = statistics.record_received(received_at)

    assert updated.observations_received == 1
    assert updated.last_observation_at == received_at


def test_record_received_does_not_modify_original_statistics() -> None:
    received_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    statistics = RuntimeStatistics()

    statistics.record_received(received_at)

    assert statistics.observations_received == 0
    assert statistics.last_observation_at is None


def test_record_accepted_updates_statistics() -> None:
    received_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    statistics = RuntimeStatistics().record_received(received_at)

    updated = statistics.record_accepted()

    assert updated.observations_accepted == 1
    assert updated.observations_processed == 1
    assert updated.observations_pending == 0


def test_record_rejected_updates_statistics() -> None:
    received_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    statistics = RuntimeStatistics().record_received(received_at)

    updated = statistics.record_rejected()

    assert updated.observations_rejected == 1
    assert updated.observations_processed == 1
    assert updated.observations_pending == 0


def test_received_observation_is_pending_until_processed() -> None:
    received_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)

    statistics = RuntimeStatistics().record_received(received_at)

    assert statistics.observations_pending == 1


def test_acceptance_rate_uses_processed_observations() -> None:
    first_received_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    second_received_at = datetime(2026, 7, 10, 14, 1, tzinfo=UTC)

    statistics = RuntimeStatistics()
    statistics = statistics.record_received(first_received_at)
    statistics = statistics.record_accepted()
    statistics = statistics.record_received(second_received_at)
    statistics = statistics.record_rejected()

    assert statistics.acceptance_rate == 0.5


def test_record_accepted_requires_received_observation() -> None:
    statistics = RuntimeStatistics()

    with pytest.raises(
        ValueError,
        match="Cannot accept an observation that has not been received",
    ):
        statistics.record_accepted()


def test_record_rejected_requires_received_observation() -> None:
    statistics = RuntimeStatistics()

    with pytest.raises(
        ValueError,
        match="Cannot reject an observation that has not been received",
    ):
        statistics.record_rejected()


def test_record_error_updates_statistics() -> None:
    occurred_at = datetime(2026, 7, 10, 14, 5, tzinfo=UTC)
    statistics = RuntimeStatistics()

    updated = statistics.record_error(occurred_at)

    assert updated.errors == 1
    assert updated.last_error_at == occurred_at


def test_multiple_events_are_accumulated() -> None:
    first_received_at = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    second_received_at = datetime(2026, 7, 10, 14, 1, tzinfo=UTC)
    error_at = datetime(2026, 7, 10, 14, 2, tzinfo=UTC)

    statistics = RuntimeStatistics()
    statistics = statistics.record_received(first_received_at)
    statistics = statistics.record_accepted()
    statistics = statistics.record_received(second_received_at)
    statistics = statistics.record_rejected()
    statistics = statistics.record_error(error_at)

    assert statistics.observations_received == 2
    assert statistics.observations_accepted == 1
    assert statistics.observations_rejected == 1
    assert statistics.observations_processed == 2
    assert statistics.observations_pending == 0
    assert statistics.errors == 1
    assert statistics.last_observation_at == second_received_at
    assert statistics.last_error_at == error_at