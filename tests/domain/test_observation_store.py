from datetime import UTC, datetime, timedelta

import pytest

from ohanna_vision.domain import (
    DuplicateObservationError,
    HealthStatus,
    Observation,
    ObservationStore,
)


def make_observation(
    *,
    observed_at: datetime | None = None,
    capability_id: str = "dns.resolve",
) -> Observation:
    return Observation(
        capability_id=capability_id,
        service_id="dns-primary",
        node_id="zwave-01",
        status=HealthStatus.HEALTHY,
        observed_at=observed_at or datetime(2026, 7, 10, 14, 0, tzinfo=UTC),
    )


def test_store_is_initially_empty() -> None:
    store = ObservationStore()

    assert store.observation_count == 0
    assert store.observations == ()


def test_store_adds_observation() -> None:
    store = ObservationStore()
    observation = make_observation()

    result = store.add(observation)

    assert result is observation
    assert store.observations == (observation,)


def test_store_rejects_duplicate_observation() -> None:
    store = ObservationStore()
    observation = make_observation()

    store.add(observation)

    with pytest.raises(DuplicateObservationError):
        store.add(observation)


def test_store_adds_many_observations() -> None:
    store = ObservationStore()
    first = make_observation(capability_id="dns.resolve")
    second = make_observation(capability_id="dns.latency")

    result = store.add_many([first, second])

    assert result == (first, second)
    assert store.observation_count == 2


def test_history_filters_observations() -> None:
    store = ObservationStore()
    first = make_observation(capability_id="dns.resolve")
    second = make_observation(capability_id="dns.latency")

    store.add_many([first, second])

    assert store.history(capability_id="dns.resolve") == (first,)


def test_history_is_chronological() -> None:
    store = ObservationStore()
    first_date = datetime(2026, 7, 10, 14, 0, tzinfo=UTC)
    second_date = first_date + timedelta(minutes=5)

    second = make_observation(observed_at=second_date)
    first = make_observation(observed_at=first_date)

    store.add_many([second, first])

    assert store.history() == (first, second)


def test_clear_removes_all_observations() -> None:
    store = ObservationStore()
    store.add(make_observation())

    store.clear()

    assert store.observation_count == 0
    assert store.observations == ()
