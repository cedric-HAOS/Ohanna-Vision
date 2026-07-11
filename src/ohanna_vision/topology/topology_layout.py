"""Layout of the Ohanna-House infrastructure topology."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite
from types import MappingProxyType

from ohanna_vision.topology.immutable import freeze_mapping
from ohanna_vision.topology.topology_layout_kind import (
    TopologyLayoutKind,
)
from ohanna_vision.topology.topology_position import (
    TopologyPosition,
)


@dataclass(frozen=True, slots=True)
class TopologyLayout:
    """Describe how topology devices are arranged on a visual canvas.

    A layout contains stable presentation coordinates only. It remains
    independent from frontend technologies and runtime health information.
    """

    layout_id: str
    label: str
    kind: TopologyLayoutKind
    positions: Mapping[str, TopologyPosition] = field(
        default_factory=dict
    )
    canvas_width: float = 1600
    canvas_height: float = 900
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and normalize the topology layout."""
        layout_id = self.layout_id.strip()
        label = self.label.strip()

        if not layout_id:
            raise ValueError("layout_id must not be empty")

        if not label:
            raise ValueError("label must not be empty")

        self._validate_dimension(
            name="canvas_width",
            value=self.canvas_width,
        )
        self._validate_dimension(
            name="canvas_height",
            value=self.canvas_height,
        )

        normalized_positions: dict[str, TopologyPosition] = {}

        for device_id, position in self.positions.items():
            normalized_device_id = device_id.strip()

            if not normalized_device_id:
                raise ValueError(
                    "position device_id must not be empty"
                )

            if normalized_device_id in normalized_positions:
                raise ValueError(
                    "position device identifiers must be unique"
                )

            normalized_positions[normalized_device_id] = position

        object.__setattr__(self, "layout_id", layout_id)
        object.__setattr__(self, "label", label)
        object.__setattr__(
            self,
            "positions",
            MappingProxyType(normalized_positions),
        )
        object.__setattr__(
            self,
            "metadata",
            freeze_mapping(self.metadata),
        )

    def position_for(
        self,
        device_id: str,
    ) -> TopologyPosition | None:
        """Return the position associated with a topology device."""
        normalized_device_id = device_id.strip()

        if not normalized_device_id:
            return None

        return self.positions.get(normalized_device_id)

    def contains_device(self, device_id: str) -> bool:
        """Return whether the layout contains a device position."""
        return self.position_for(device_id) is not None

    @staticmethod
    def _validate_dimension(
        *,
        name: str,
        value: float,
    ) -> None:
        """Validate a canvas dimension."""
        if not isfinite(value):
            raise ValueError(f"{name} must be finite")

        if value <= 0:
            raise ValueError(
                f"{name} must be greater than zero"
            )