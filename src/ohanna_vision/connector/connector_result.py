"""Result returned by an observation connector."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class ConnectorResult:
    """Represent the outcome of an observation reception."""

    success: bool
    message: str

    @classmethod
    def succeeded(
        cls,
        message: str = "Observation received successfully.",
    ) -> "ConnectorResult":
        """Create a successful connector result."""
        return cls(
            success=True,
            message=message,
        )

    @classmethod
    def failed(
        cls,
        message: str,
    ) -> "ConnectorResult":
        """Create a failed connector result."""
        return cls(
            success=False,
            message=message,
        )