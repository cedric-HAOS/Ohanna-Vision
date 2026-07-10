"""Shared validation rules for timeline periods."""

from ohanna_vision.timeline.state_period import StatePeriod


def validate_periods(
    periods: tuple[StatePeriod, ...],
) -> None:
    """Validate ordering and continuity of timeline periods."""

    for index, period in enumerate(periods):
        if period.is_open and index != len(periods) - 1:
            raise ValueError("Only the last period may be open.")

    for previous, current in zip(
        periods,
        periods[1:],
        strict=False,
    ):
        if current.started_at < previous.started_at:
            raise ValueError(
                "Periods must be ordered chronologically."
            )

        if previous.ended_at is None:
            raise ValueError(
                "An open period cannot be followed by another period."
            )

        if current.started_at < previous.ended_at:
            raise ValueError("Periods must not overlap.")

        if current.started_at > previous.ended_at:
            raise ValueError("Periods must be contiguous.")

        if current.status is previous.status:
            raise ValueError(
                "Consecutive periods must have different statuses."
            )