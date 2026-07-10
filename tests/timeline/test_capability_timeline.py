from datetime import UTC, datetime, timedelta

import pytest

from ohanna_vision.domain import HealthStatus
from ohanna_vision.timeline import CapabilityTimeline, StatePeriod


def make_period(
    status: HealthStatus,
    started_at: datetime,
    ended_at: datetime | None = None,
) -> StatePeriod:
    return StatePeriod(
        status=status,
        started_at=started_at,
        ended_at=ended_at,
    )


def test_empty_capability_timeline_is_created() -> None:
    timeline = CapabilityTimeline(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="infra-01",
    )

    assert timeline.periods == ()
    assert timeline.is_empty is True
    assert timeline.first_period is None
    assert timeline.last_period is None
    assert timeline.current_period is None
    assert timeline.current_status is None
    assert timeline.started_at is None
    assert timeline.ended_at is None
    assert timeline.transition_count == 0
    assert timeline.incident_count == 0


def test_active_capability_timeline_is_created() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    period = make_period(
        HealthStatus.HEALTHY,
        started_at,
    )

    timeline = CapabilityTimeline(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="infra-01",
        periods=(period,),
    )

    assert timeline.is_empty is False
    assert timeline.first_period is period
    assert timeline.last_period is period
    assert timeline.current_period is period
    assert timeline.current_status is HealthStatus.HEALTHY
    assert timeline.started_at == started_at
    assert timeline.ended_at is None


def test_closed_capability_timeline_has_end_date() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    ended_at = started_at + timedelta(minutes=15)

    period = make_period(
        HealthStatus.HEALTHY,
        started_at,
        ended_at,
    )

    timeline = CapabilityTimeline(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="infra-01",
        periods=(period,),
    )

    assert timeline.current_period is None
    assert timeline.current_status is None
    assert timeline.ended_at == ended_at


def test_timeline_exposes_transitions_and_incidents() -> None:
    first_date = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    second_date = first_date + timedelta(minutes=15)
    third_date = second_date + timedelta(minutes=10)

    healthy = make_period(
        HealthStatus.HEALTHY,
        first_date,
        second_date,
    )
    degraded = make_period(
        HealthStatus.DEGRADED,
        second_date,
        third_date,
    )
    recovered = make_period(
        HealthStatus.HEALTHY,
        third_date,
    )

    timeline = CapabilityTimeline(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="infra-01",
        periods=(healthy, degraded, recovered),
    )

    assert timeline.transition_count == 2
    assert timeline.incident_periods == (degraded,)
    assert timeline.incident_count == 1
    assert timeline.current_status is HealthStatus.HEALTHY


def test_period_at_returns_matching_period() -> None:
    first_date = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    transition_date = first_date + timedelta(minutes=15)

    healthy = make_period(
        HealthStatus.HEALTHY,
        first_date,
        transition_date,
    )
    degraded = make_period(
        HealthStatus.DEGRADED,
        transition_date,
    )

    timeline = CapabilityTimeline(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="infra-01",
        periods=(healthy, degraded),
    )

    assert timeline.period_at(
        first_date + timedelta(minutes=5)
    ) is healthy

    assert timeline.period_at(transition_date) is degraded


def test_status_at_returns_matching_status() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    timeline = CapabilityTimeline(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="infra-01",
        periods=(
            make_period(
                HealthStatus.DEGRADED,
                started_at,
            ),
        ),
    )

    assert timeline.status_at(
        started_at + timedelta(minutes=5)
    ) is HealthStatus.DEGRADED


def test_period_at_returns_none_outside_timeline() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    timeline = CapabilityTimeline(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="infra-01",
        periods=(
            make_period(
                HealthStatus.HEALTHY,
                started_at,
            ),
        ),
    )

    assert timeline.period_at(
        started_at - timedelta(minutes=1)
    ) is None


def test_current_duration_returns_open_period_duration() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    timeline = CapabilityTimeline(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="infra-01",
        periods=(
            make_period(
                HealthStatus.HEALTHY,
                started_at,
            ),
        ),
    )

    assert timeline.current_duration(
        started_at + timedelta(minutes=20)
    ) == timedelta(minutes=20)


def test_current_duration_returns_none_without_open_period() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    timeline = CapabilityTimeline(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="infra-01",
        periods=(
            make_period(
                HealthStatus.HEALTHY,
                started_at,
                started_at + timedelta(minutes=15),
            ),
        ),
    )

    assert timeline.current_duration(
        started_at + timedelta(minutes=20)
    ) is None


def test_periods_with_status_filters_periods() -> None:
    first_date = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    second_date = first_date + timedelta(minutes=10)
    third_date = second_date + timedelta(minutes=10)

    first_healthy = make_period(
        HealthStatus.HEALTHY,
        first_date,
        second_date,
    )
    degraded = make_period(
        HealthStatus.DEGRADED,
        second_date,
        third_date,
    )
    second_healthy = make_period(
        HealthStatus.HEALTHY,
        third_date,
    )

    timeline = CapabilityTimeline(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="infra-01",
        periods=(
            first_healthy,
            degraded,
            second_healthy,
        ),
    )

    assert timeline.periods_with_status(
        HealthStatus.HEALTHY
    ) == (
        first_healthy,
        second_healthy,
    )


def test_timeline_rejects_non_contiguous_periods() -> None:
    first_date = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    first_end = first_date + timedelta(minutes=10)
    second_start = first_end + timedelta(minutes=5)

    with pytest.raises(
        ValueError,
        match="Periods must be contiguous",
    ):
        CapabilityTimeline(
            capability_id="dns.resolve",
            service_id="dns-primary",
            node_id="infra-01",
            periods=(
                make_period(
                    HealthStatus.HEALTHY,
                    first_date,
                    first_end,
                ),
                make_period(
                    HealthStatus.DEGRADED,
                    second_start,
                ),
            ),
        )


def test_timeline_rejects_overlapping_periods() -> None:
    first_date = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    first_end = first_date + timedelta(minutes=15)
    second_start = first_date + timedelta(minutes=10)

    with pytest.raises(
        ValueError,
        match="Periods must not overlap",
    ):
        CapabilityTimeline(
            capability_id="dns.resolve",
            service_id="dns-primary",
            node_id="infra-01",
            periods=(
                make_period(
                    HealthStatus.HEALTHY,
                    first_date,
                    first_end,
                ),
                make_period(
                    HealthStatus.DEGRADED,
                    second_start,
                ),
            ),
        )


def test_timeline_rejects_open_period_before_last_position() -> None:
    started_at = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)

    with pytest.raises(
        ValueError,
        match="Only the last period may be open",
    ):
        CapabilityTimeline(
            capability_id="dns.resolve",
            service_id="dns-primary",
            node_id="infra-01",
            periods=(
                make_period(
                    HealthStatus.HEALTHY,
                    started_at,
                ),
                make_period(
                    HealthStatus.DEGRADED,
                    started_at + timedelta(minutes=10),
                ),
            ),
        )


def test_timeline_rejects_consecutive_identical_statuses() -> None:
    first_date = datetime(2026, 7, 10, 8, 0, tzinfo=UTC)
    transition_date = first_date + timedelta(minutes=10)

    with pytest.raises(
        ValueError,
        match="Consecutive periods must have different statuses",
    ):
        CapabilityTimeline(
            capability_id="dns.resolve",
            service_id="dns-primary",
            node_id="infra-01",
            periods=(
                make_period(
                    HealthStatus.HEALTHY,
                    first_date,
                    transition_date,
                ),
                make_period(
                    HealthStatus.HEALTHY,
                    transition_date,
                ),
            ),
        )


def test_timeline_rejects_empty_identifier() -> None:
    with pytest.raises(
        ValueError,
        match="capability_id must not be empty",
    ):
        CapabilityTimeline(
            capability_id=" ",
            service_id="dns-primary",
            node_id="infra-01",
        )


def test_period_at_rejects_naive_instant() -> None:
    timeline = CapabilityTimeline(
        capability_id="dns.resolve",
        service_id="dns-primary",
        node_id="infra-01",
    )

    with pytest.raises(
        ValueError,
        match="instant must be timezone-aware",
    ):
        timeline.period_at(datetime(2026, 7, 10, 8, 0))