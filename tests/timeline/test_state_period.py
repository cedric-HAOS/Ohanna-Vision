from datetime import UTC, datetime, timedelta

import pytest

from ohana_vision.domain import HealthStatus
from ohana_vision.timeline import StatePeriod


def test_open_state_period_is_created() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    period = StatePeriod(
        status=HealthStatus.HEALTHY,
        started_at=started_at,
    )

    assert period.status is HealthStatus.HEALTHY
    assert period.started_at == started_at
    assert period.ended_at is None
    assert period.is_open is True
    assert period.is_closed is False


def test_closed_state_period_is_created() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    ended_at = started_at + timedelta(minutes=15)

    period = StatePeriod(
        status=HealthStatus.DEGRADED,
        started_at=started_at,
        ended_at=ended_at,
    )

    assert period.is_open is False
    assert period.is_closed is True
    assert period.duration == timedelta(minutes=15)
    assert period.duration_seconds == 900.0


def test_open_period_has_no_fixed_duration() -> None:
    period = StatePeriod(
        status=HealthStatus.HEALTHY,
        started_at=datetime(2026, 7, 10, 8, 0, tzinfo=UTC),
    )

    assert period.duration is None
    assert period.duration_seconds is None


def test_duration_at_calculates_open_period_duration() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    period = StatePeriod(
        status=HealthStatus.HEALTHY,
        started_at=started_at,
    )

    duration = period.duration_at(started_at + timedelta(minutes=15))

    assert duration == timedelta(minutes=15)


def test_duration_at_returns_fixed_closed_duration() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    period = StatePeriod(
        status=HealthStatus.HEALTHY,
        started_at=started_at,
        ended_at=started_at + timedelta(minutes=15),
    )

    duration = period.duration_at(started_at + timedelta(hours=1))

    assert duration == timedelta(minutes=15)


def test_period_contains_start_date() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    period = StatePeriod(
        status=HealthStatus.HEALTHY,
        started_at=started_at,
        ended_at=started_at + timedelta(minutes=15),
    )

    assert period.contains(started_at) is True


def test_closed_period_does_not_contain_end_date() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    ended_at = started_at + timedelta(minutes=15)

    period = StatePeriod(
        status=HealthStatus.HEALTHY,
        started_at=started_at,
        ended_at=ended_at,
    )

    assert period.contains(ended_at) is False


def test_open_period_contains_later_date() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    period = StatePeriod(
        status=HealthStatus.HEALTHY,
        started_at=started_at,
    )

    assert period.contains(started_at + timedelta(days=1)) is True


def test_close_returns_new_closed_period() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    ended_at = started_at + timedelta(minutes=15)

    period = StatePeriod(
        status=HealthStatus.HEALTHY,
        started_at=started_at,
    )

    closed = period.close(ended_at)

    assert period.is_open is True
    assert closed.is_closed is True
    assert closed.started_at == started_at
    assert closed.ended_at == ended_at
    assert closed.status is HealthStatus.HEALTHY


def test_closed_period_cannot_be_closed_again() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    period = StatePeriod(
        status=HealthStatus.HEALTHY,
        started_at=started_at,
        ended_at=started_at + timedelta(minutes=15),
    )

    with pytest.raises(
        ValueError,
        match="A closed period cannot be closed again",
    ):
        period.close(started_at + timedelta(minutes=30))


def test_period_rejects_naive_start_date() -> None:
    with pytest.raises(
        ValueError,
        match="started_at must be timezone-aware",
    ):
        StatePeriod(
            status=HealthStatus.HEALTHY,
            started_at=datetime(2026, 7, 10, 8, 0),
        )


def test_period_rejects_naive_end_date() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    with pytest.raises(
        ValueError,
        match="ended_at must be timezone-aware",
    ):
        StatePeriod(
            status=HealthStatus.HEALTHY,
            started_at=started_at,
            ended_at=datetime(2026, 7, 10, 8, 15),
        )


def test_period_rejects_end_before_start() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    with pytest.raises(
        ValueError,
        match="ended_at must not be before started_at",
    ):
        StatePeriod(
            status=HealthStatus.HEALTHY,
            started_at=started_at,
            ended_at=started_at - timedelta(minutes=1),
        )


def test_duration_at_rejects_naive_instant() -> None:
    period = StatePeriod(
        status=HealthStatus.HEALTHY,
        started_at=datetime(2026, 7, 10, 8, 0, tzinfo=UTC),
    )

    with pytest.raises(
        ValueError,
        match="instant must be timezone-aware",
    ):
        period.duration_at(datetime(2026, 7, 10, 8, 15))


def test_duration_at_rejects_instant_before_start() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    period = StatePeriod(
        status=HealthStatus.HEALTHY,
        started_at=started_at,
    )

    with pytest.raises(
        ValueError,
        match="instant must not be before started_at",
    ):
        period.duration_at(started_at - timedelta(minutes=1))
