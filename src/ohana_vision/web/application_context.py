"""Application services exposed to the web layer."""

from dataclasses import dataclass

from ohana_vision.domain import ObservationStore
from ohana_vision.runtime import BackendRuntime
from ohana_vision.timeline import TimelineEngine


@dataclass(frozen=True, slots=True)
class ApplicationContext:
    """Services required by the Ohana-Vision web application."""

    runtime: BackendRuntime
    observation_store: ObservationStore
    timeline_engine: TimelineEngine
