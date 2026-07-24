"""Administration gateway from Vision to Ohana-Agent."""

from ohana_vision.administration.client import (
    AgentAdministrationClient,
    AgentAdministrationError,
)

__all__ = [
    "AgentAdministrationClient",
    "AgentAdministrationError",
]
