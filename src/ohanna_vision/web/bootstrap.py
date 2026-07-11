"""Application composition for Ohanna-Vision."""

from fastapi import FastAPI

from ohanna_vision.domain import ObservationStore
from ohanna_vision.runtime import BackendRuntime
from ohanna_vision.timeline import TimelineEngine
from ohanna_vision.web.app import create_app
from ohanna_vision.web.application_context import ApplicationContext


def build_application_context() -> ApplicationContext:
    """Build the default Ohanna-Vision application context."""
    runtime = BackendRuntime()
    observation_store = ObservationStore()
    timeline_engine = TimelineEngine()

    return ApplicationContext(
        runtime=runtime,
        observation_store=observation_store,
        timeline_engine=timeline_engine,
    )


def build_application() -> FastAPI:
    """Build the complete Ohanna-Vision web application."""
    context = build_application_context()

    return create_app(context=context)


app = build_application()