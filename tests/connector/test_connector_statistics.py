"""Tests for ConnectorStatistics."""

from datetime import UTC, datetime

from ohanna_vision.connector import ConnectorStatistics


def make_instant() -> datetime:
    """Return a stable timezone-aware instant for tests."""
    return datetime(2026, 7, 11, 12, 0, tzinfo=UTC)


def test_connector_statistics_starts_empty() -> None:
    statistics = ConnectorStatistics()

    assert statistics.received_count == 0
    assert statistics.failed_count == 0
    assert statistics.successful_count == 0
    assert statistics.last_received_at is None


def test_connector_statistics_records_success() -> None:
    statistics = ConnectorStatistics()
    received_at = make_instant()

    statistics.record_success(received_at)

    assert statistics.received_count == 1
    assert statistics.failed_count == 0
    assert statistics.successful_count == 1
    assert statistics.last_received_at is received_at


def test_connector_statistics_records_multiple_successes() -> None:
    statistics = ConnectorStatistics()
    received_at = make_instant()

    statistics.record_success(received_at)
    statistics.record_success(received_at)

    assert statistics.received_count == 2
    assert statistics.failed_count == 0
    assert statistics.successful_count == 2


def test_connector_statistics_records_failure() -> None:
    statistics = ConnectorStatistics()
    received_at = make_instant()

    statistics.record_failure(received_at)

    assert statistics.received_count == 1
    assert statistics.failed_count == 1
    assert statistics.successful_count == 0
    assert statistics.last_received_at is received_at


def test_connector_statistics_counts_successes_and_failures() -> None:
    statistics = ConnectorStatistics()
    received_at = make_instant()

    statistics.record_success(received_at)
    statistics.record_failure(received_at)
    statistics.record_success(received_at)

    assert statistics.received_count == 3
    assert statistics.failed_count == 1
    assert statistics.successful_count == 2


def test_connector_statistics_updates_last_received_at() -> None:
    statistics = ConnectorStatistics()
    first_received_at = datetime(2026, 7, 11, 12, 0, tzinfo=UTC)
    second_received_at = datetime(2026, 7, 11, 12, 5, tzinfo=UTC)

    statistics.record_success(first_received_at)
    statistics.record_failure(second_received_at)

    assert statistics.last_received_at is second_received_at


def test_connector_statistics_can_be_reset() -> None:
    statistics = ConnectorStatistics()
    received_at = make_instant()

    statistics.record_success(received_at)
    statistics.record_failure(received_at)

    statistics.reset()

    assert statistics.received_count == 0
    assert statistics.failed_count == 0
    assert statistics.successful_count == 0
    assert statistics.last_received_at is None
