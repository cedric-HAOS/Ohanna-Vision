"""Tests for the Ohanna-Vision application bootstrap."""

from fastapi import FastAPI
from fastapi.testclient import TestClient

from ohanna_vision.domain import ObservationStore
from ohanna_vision.runtime import BackendRuntime
from ohanna_vision.timeline import TimelineEngine
from ohanna_vision.web.app import create_app
from ohanna_vision.web.application_context import ApplicationContext
from ohanna_vision.web.bootstrap import (
    build_application,
    build_application_context,
)


def test_build_application_context_returns_context() -> None:
    """The bootstrap must build an application context."""
    context = build_application_context()

    assert isinstance(context, ApplicationContext)


def test_build_application_context_contains_runtime() -> None:
    """The context must contain a backend runtime."""
    context = build_application_context()

    assert isinstance(context.runtime, BackendRuntime)


def test_build_application_context_contains_observation_store() -> None:
    """The context must contain an observation store."""
    context = build_application_context()

    assert isinstance(
        context.observation_store,
        ObservationStore,
    )


def test_build_application_context_contains_timeline_engine() -> None:
    """The context must contain a timeline engine."""
    context = build_application_context()

    assert isinstance(
        context.timeline_engine,
        TimelineEngine,
    )

def test_build_application_returns_fastapi() -> None:
    """The bootstrap must create the complete FastAPI application."""
    app = build_application()

    assert isinstance(app, FastAPI)

def test_build_application_stores_built_context() -> None:
    """The application must retain its composed context."""
    context = build_application_context()

    app = create_app(context=context)

    assert app.state.context is context
    assert app.state.context.runtime is context.runtime
    assert (
        app.state.context.observation_store
        is context.observation_store
    )
    assert (
        app.state.context.timeline_engine
        is context.timeline_engine
    )

def test_bootstrapped_runtime_api_is_available() -> None:
    """The complete application must expose its runtime."""
    client = TestClient(build_application())

    response = client.get("/api/runtime")

    assert response.status_code == 200
    assert response.json()["state"] == "created"


def test_bootstrapped_observation_api_is_available() -> None:
    """The complete application must expose its observation store."""
    client = TestClient(build_application())

    response = client.get("/api/observations")

    assert response.status_code == 200
    assert response.json() == []


def test_bootstrapped_timeline_api_is_available() -> None:
    """The complete application must expose its timeline."""
    client = TestClient(build_application())

    response = client.get("/api/timeline")

    assert response.status_code == 200
    assert response.json() == {
        "nodes": [],
        "periods": [],
    }