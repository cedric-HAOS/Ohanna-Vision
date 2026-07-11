"""Application services exposed to the web layer."""

from dataclasses import dataclass

from ohanna_vision.domain import ObservationStore
from ohanna_vision.runtime import BackendRuntime
from ohanna_vision.timeline import TimelineEngine


@dataclass(frozen=True, slots=True)
class ApplicationContext:
    """Services required by the Ohanna-Vision web application."""

    runtime: BackendRuntime
    observation_store: ObservationStore
    timeline_engine: TimelineEngine