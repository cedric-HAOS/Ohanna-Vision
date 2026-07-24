"""Executable FastAPI application for Ohana-Vision."""

from ohana_vision.domain.observation_store import ObservationStore
from ohana_vision.runtime import BackendRuntime
from ohana_vision.timeline import TimelineEngine
from ohana_vision.web import create_app


def build_runtime() -> BackendRuntime:
    """Build the default Ohana-Vision backend runtime."""
    return BackendRuntime(
        observation_store=ObservationStore(),
        timeline_engine=TimelineEngine(),
    )


app = create_app(build_runtime())
