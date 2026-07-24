"""Backend runtime lifecycle states."""

from enum import StrEnum


class BackendRuntimeState(StrEnum):
    """Lifecycle state of the Ohana-Vision backend runtime."""

    CREATED = "created"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"

    @property
    def active(self) -> bool:
        """Return whether the backend is active."""

        return self in {
            BackendRuntimeState.STARTING,
            BackendRuntimeState.RUNNING,
            BackendRuntimeState.STOPPING,
        }

    @property
    def terminal(self) -> bool:
        """Return whether the backend reached a terminal state."""

        return self in {
            BackendRuntimeState.STOPPED,
            BackendRuntimeState.FAILED,
        }

    @property
    def healthy(self) -> bool:
        """Return whether the backend is operational."""

        return self is BackendRuntimeState.RUNNING
