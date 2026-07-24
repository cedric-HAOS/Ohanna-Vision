"""Tests for the Ohana-Vision application context."""

from typing import cast

from ohana_vision.domain.observation_store import ObservationStore
from ohana_vision.runtime import BackendRuntime
from ohana_vision.timeline import TimelineEngine
from ohana_vision.web import ApplicationContext


def test_application_context_exposes_services() -> None:
    """The context must retain every injected service."""
    runtime = cast(BackendRuntime, object())
    observation_store = cast(ObservationStore, object())
    timeline_engine = cast(TimelineEngine, object())

    context = ApplicationContext(
        runtime=runtime,
        observation_store=observation_store,
        timeline_engine=timeline_engine,
    )

    assert context.runtime is runtime
    assert context.observation_store is observation_store
    assert context.timeline_engine is timeline_engine
