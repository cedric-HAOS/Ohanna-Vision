"""Lifecycle states for an observation connector."""

from enum import StrEnum


class ConnectorState(StrEnum):
    """Represent the lifecycle state of a connector."""

    CREATED = "created"
    READY = "ready"
    RUNNING = "running"
    ERROR = "error"
