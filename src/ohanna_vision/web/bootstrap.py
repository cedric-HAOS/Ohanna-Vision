"""Application composition for Ohanna-Vision."""

from fastapi import FastAPI

from ohanna_vision.domain import ObservationStore
from ohanna_vision.runtime import BackendRuntime
from ohanna_vision.timeline import TimelineEngine
from ohanna_vision.topology import (
    build_ohanna_house_topology,
)
from ohanna_vision.web.app import create_app
from ohanna_vision.web.application_context import ApplicationContext
from ohanna_vision.web.dependencies import get_topology


def build_application_context() -> ApplicationContext:
    """Build the default Ohanna-Vision application context."""
    runtime = BackendRuntime()
    observation_store = ObservationStore()
    timeline_engine = TimelineEngine()

    runtime.start()

    return ApplicationContext(
        runtime=runtime,
        observation_store=observation_store,
        timeline_engine=timeline_engine,
    )


def build_application() -> FastAPI:
    """Build the fully configured Ohanna-Vision application."""
    context = build_application_context()
    topology = build_ohanna_house_topology()

    application = create_app(
        context=context,
    )

    application.dependency_overrides[
        get_topology
    ] = lambda: topology

    return application


app = build_application()