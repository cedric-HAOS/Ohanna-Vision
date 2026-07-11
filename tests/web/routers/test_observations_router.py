"""Tests for the Ohanna-Vision observation API router."""

from datetime import UTC, datetime
from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ohanna_vision.domain.health import HealthStatus
from ohanna_vision.domain.observation import Observation
from ohanna_vision.domain.observation_store import ObservationStore
from ohanna_vision.web.dependencies import get_observation_store
from ohanna_vision.web.routers import observations_router


class FakeObservationStore:
    """Observation store double exposing fixed history results."""

    def __init__(
        self,
        observations: tuple[Observation, ...] = (),
    ) -> None:
        self._observations = observations
        self.history_calls: list[dict[str, object]] = []

    def history(
        self,
        *,
        node_id: str | None = None,
        service_id: str | None = None,
        capability_id: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> tuple[Observation, ...]:
        """Return the configured observations."""
        self.history_calls.append(
            {
                "node_id": node_id,
                "service_id": service_id,
                "capability_id": capability_id,
                "since": since,
                "until": until,
            }
        )

        return self._observations
    
def make_observation(
    *,
    capability_id: str = "dns-resolution",
    service_id: str = "dns-primary",
    node_id: str = "infra-01",
    status: HealthStatus = HealthStatus.HEALTHY,
    observed_at: datetime | None = None,
    latency_ms: float | None = 4.2,
) -> Observation:
    """Create an observation for API tests."""
    return Observation(
        capability_id=capability_id,
        service_id=service_id,
        node_id=node_id,
        status=status,
        observed_at=observed_at
        or datetime(2026, 7, 11, 12, 0, tzinfo=UTC),
        latency_ms=latency_ms,
        metadata={},
    )

def make_client(
    store: FakeObservationStore,
) -> TestClient:
    """Create a client with an overridden observation store."""
    app = FastAPI()
    app.include_router(observations_router)

    app.dependency_overrides[get_observation_store] = lambda: cast(
        ObservationStore,
        store,
    )

    return TestClient(app)

def test_observations_router_returns_empty_list() -> None:
    """The endpoint must return an empty list when no history exists."""
    client = make_client(FakeObservationStore())

    response = client.get("/observations")

    assert response.status_code == 200
    assert response.json() == []

def test_observations_router_returns_stored_observations() -> None:
    """The endpoint must return observations provided by the store."""
    first = make_observation()
    second = make_observation(
        capability_id="internet-access",
        service_id="internet-primary",
        status=HealthStatus.DEGRADED,
        latency_ms=42.5,
    )
    client = make_client(
        FakeObservationStore((first, second)),
    )

    response = client.get("/observations")

    assert response.status_code == 200
    assert len(response.json()) == 2

def test_observations_router_passes_filters_to_store() -> None:
    """The endpoint must delegate all filters to the store."""
    store = FakeObservationStore()
    client = make_client(store)

    response = client.get(
        "/observations",
        params={
            "node_id": "infra-01",
            "service_id": "dns-primary",
            "capability_id": "dns-resolution",
            "since": "2026-07-11T10:00:00Z",
            "until": "2026-07-11T12:00:00Z",
        },
    )

    assert response.status_code == 200
    assert store.history_calls == [
        {
            "node_id": "infra-01",
            "service_id": "dns-primary",
            "capability_id": "dns-resolution",
            "since": datetime(
                2026,
                7,
                11,
                10,
                0,
                tzinfo=UTC,
            ),
            "until": datetime(
                2026,
                7,
                11,
                12,
                0,
                tzinfo=UTC,
            ),
        }
    ]

class InvalidHistoryObservationStore(FakeObservationStore):
    """Observation store double rejecting history filters."""

    def history(
        self,
        *,
        node_id: str | None = None,
        service_id: str | None = None,
        capability_id: str | None = None,
        since: datetime | None = None,
        until: datetime | None = None,
    ) -> tuple[Observation, ...]:
        """Reject invalid date ordering."""
        raise ValueError("since must not be after until.")

def test_observations_router_returns_422_for_invalid_history() -> None:
    """Domain validation errors must become HTTP 422 responses."""
    client = make_client(InvalidHistoryObservationStore())

    response = client.get(
        "/observations",
        params={
            "since": "2026-07-11T12:00:00Z",
            "until": "2026-07-11T10:00:00Z",
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "since must not be after until.",
    }

def test_observations_router_returns_503_without_context() -> None:
    """The endpoint must fail explicitly without application context."""
    app = FastAPI()
    app.include_router(observations_router)

    response = TestClient(app).get("/observations")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Application context is not configured",
    }