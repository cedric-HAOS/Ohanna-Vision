"""Position of a device in an infrastructure topology layout."""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True, slots=True)
class TopologyPosition:
    """Describe the position of a device on a topology canvas."""

    x: float
    y: float
    layer: int = 0
    pinned: bool = False

    def __post_init__(self) -> None:
        """Validate the topology position."""
        if not isfinite(self.x):
            raise ValueError("x must be finite")

        if not isfinite(self.y):
            raise ValueError("y must be finite")
