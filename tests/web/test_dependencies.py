"""Tests for Ohanna-Vision FastAPI dependencies."""

from typing import cast

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ohanna_vision.domain.observation_store import ObservationStore
from ohanna_vision.runtime import BackendRuntime
from ohanna_vision.timeline import TimelineEngine
from ohanna_vision.web import (
    ApplicationContext,
    ApplicationContextDependency,
    ObservationStoreDependency,
    RuntimeDependency,
    TimelineEngineDependency,
    get_application_context,
)


def make_context() -> ApplicationContext:
    """Create an application context without constructing real services."""
    return ApplicationContext(
        runtime=cast(BackendRuntime, object()),
        observation_store=cast(ObservationStore, object()),
        timeline_engine=cast(TimelineEngine, object()),
    )


def test_application_context_dependency_returns_attached_context() -> None:
    """The dependency must return the context stored by FastAPI."""
    context = make_context()
    app = FastAPI()
    app.state.context = context

    @app.get("/context")
    def context_endpoint(
        injected_context: ApplicationContextDependency,
    ) -> dict[str, bool]:
        return {
            "same_context": injected_context is context,
        }

    response = TestClient(app).get("/context")

    assert response.status_code == 200
    assert response.json() == {
        "same_context": True,
    }


def test_application_context_dependency_returns_503_when_missing() -> None:
    """A missing context must produce an explicit service error."""
    app = FastAPI()

    @app.get("/context")
    def context_endpoint(
        context: ApplicationContextDependency,
    ) -> dict[str, bool]:
        return {
            "configured": context is not None,
        }

    response = TestClient(app).get("/context")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Application context is not configured",
    }


def test_runtime_dependency_returns_context_runtime() -> None:
    """The runtime dependency must expose the context runtime."""
    context = make_context()
    app = FastAPI()
    app.state.context = context

    @app.get("/runtime")
    def runtime_endpoint(
        runtime: RuntimeDependency,
    ) -> dict[str, bool]:
        return {
            "same_runtime": runtime is context.runtime,
        }

    response = TestClient(app).get("/runtime")

    assert response.status_code == 200
    assert response.json() == {
        "same_runtime": True,
    }


def test_observation_store_dependency_returns_context_store() -> None:
    """The store dependency must expose the context store."""
    context = make_context()
    app = FastAPI()
    app.state.context = context

    @app.get("/observation-store")
    def observation_store_endpoint(
        observation_store: ObservationStoreDependency,
    ) -> dict[str, bool]:
        return {
            "same_store": (
                observation_store is context.observation_store
            ),
        }

    response = TestClient(app).get("/observation-store")

    assert response.status_code == 200
    assert response.json() == {
        "same_store": True,
    }


def test_timeline_engine_dependency_returns_context_engine() -> None:
    """The timeline dependency must expose the context engine."""
    context = make_context()
    app = FastAPI()
    app.state.context = context

    @app.get("/timeline-engine")
    def timeline_engine_endpoint(
        timeline_engine: TimelineEngineDependency,
    ) -> dict[str, bool]:
        return {
            "same_engine": (
                timeline_engine is context.timeline_engine
            ),
        }

    response = TestClient(app).get("/timeline-engine")

    assert response.status_code == 200
    assert response.json() == {
        "same_engine": True,
    }


def test_application_context_dependency_can_be_overridden() -> None:
    """FastAPI must support overriding the context in tests."""
    original_context = make_context()
    overridden_context = make_context()

    app = FastAPI()
    app.state.context = original_context

    @app.get("/context")
    def context_endpoint(
        context: ApplicationContextDependency,
    ) -> dict[str, bool]:
        return {
            "overridden": context is overridden_context,
        }

    app.dependency_overrides[get_application_context] = (
        lambda: overridden_context
    )

    response = TestClient(app).get("/context")

    assert response.status_code == 200
    assert response.json() == {
        "overridden": True,
    }