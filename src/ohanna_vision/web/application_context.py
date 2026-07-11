"""Application service composition for Ohanna-Vision."""

from dataclasses import dataclass

from ohanna_vision.domain.observation_store import ObservationStore
from ohanna_vision.runtime import BackendRuntime
from ohanna_vision.timeline import TimelineEngine


@dataclass(frozen=True, slots=True)
class ApplicationContext:
    """Services exposed to the Ohanna-Vision web application."""

    runtime: BackendRuntime
    observation_store: ObservationStore
    timeline_engine: TimelineEngine