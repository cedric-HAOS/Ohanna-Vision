"""Tests for the Ohanna-Vision runtime API router."""

from datetime import UTC, datetime
from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ohanna_vision.runtime import (
    BackendRuntime,
    BackendRuntimeState,
    RuntimeSnapshot,
    RuntimeStatistics,
)
from ohanna_vision.web.dependencies import get_runtime
from ohanna_vision.web.routers import runtime_router


class FakeBackendRuntime:
    """Backend runtime double exposing a fixed snapshot."""

    def __init__(self, snapshot: RuntimeSnapshot) -> None:
        self._snapshot = snapshot
        self.snapshot_calls = 0

    def snapshot(self) -> RuntimeSnapshot:
        """Return the configured runtime snapshot."""
        self.snapshot_calls += 1
        return self._snapshot


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

def make_client(
    runtime: FakeBackendRuntime,
) -> TestClient:
    """Create a test client with an overridden runtime."""
    app = FastAPI()
    app.include_router(runtime_router)

    app.dependency_overrides[get_runtime] = lambda: cast(
        BackendRuntime,
        runtime,
    )

    return TestClient(app)


def test_runtime_router_returns_runtime_snapshot() -> None:
    """The runtime endpoint must expose the current snapshot."""
    snapshot = make_snapshot()
    runtime = FakeBackendRuntime(snapshot)
    client = make_client(runtime)

    response = client.get("/runtime")

    assert response.status_code == 200
    assert runtime.snapshot_calls == 1


def test_runtime_router_serializes_snapshot() -> None:
    """The runtime endpoint must serialize the complete snapshot."""
    snapshot = make_snapshot(
        observations_stored=3,
        service_timelines=2,
        node_timelines=1,
        infrastructure_timelines=1,
    )
    runtime = FakeBackendRuntime(snapshot)
    client = make_client(runtime)

    response = client.get("/runtime")

    assert response.status_code == 200
    assert response.json() == {
        "state": snapshot.state.value,
        "statistics": {
            "observations_received": 0,
            "observations_accepted": 0,
            "observations_rejected": 0,
            "errors": 0,
            "last_observation_at": None,
            "last_error_at": None,
        },
        "generated_at": snapshot.generated_at.isoformat().replace("+00:00", "Z"),
        "observations_stored": 3,
        "service_timelines": 2,
        "node_timelines": 1,
        "infrastructure_timelines": 1,
}

def test_runtime_router_exposes_runtime_state() -> None:
    """The runtime endpoint must expose the runtime state."""
    snapshot = make_snapshot()
    runtime = FakeBackendRuntime(snapshot)
    client = make_client(runtime)

    response = client.get("/runtime")

    assert response.status_code == 200
    assert response.json()["state"] == snapshot.state.value

def test_runtime_router_returns_503_without_context() -> None:
    """The runtime API must fail explicitly without application context."""
    app = FastAPI()
    app.include_router(runtime_router)

    response = TestClient(app).get("/runtime")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Application context is not configured",
    }