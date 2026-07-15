"""Processor contract required by observation connectors."""

from typing import Protocol

from ohanna_vision.domain import Observation
from ohanna_vision.runtime import ProcessingResult


class ObservationProcessorProtocol(Protocol):
    """Define the observation-processing contract used by connectors."""

    def process(
        self,
        observation: Observation,
    ) -> ProcessingResult:
        """Process an observation and return its processing result."""
        ...
