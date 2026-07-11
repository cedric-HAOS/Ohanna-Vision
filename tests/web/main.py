"""Executable FastAPI application for Ohanna-Vision."""

from ohanna_vision.domain.observation_store import ObservationStore
from ohanna_vision.runtime import BackendRuntime
from ohanna_vision.timeline import TimelineEngine
from ohanna_vision.web import create_app


def build_runtime() -> BackendRuntime:
    """Build the default Ohanna-Vision backend runtime."""
    return BackendRuntime(
        observation_store=ObservationStore(),
        timeline_engine=TimelineEngine(),
    )


app = create_app(build_runtime())