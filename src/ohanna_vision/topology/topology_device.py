"""Device represented in the Ohanna-House infrastructure topology."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from ohanna_vision.topology.immutable import freeze_mapping
from ohanna_vision.topology.topology_device_kind import (
    TopologyDeviceKind,
)


@dataclass(frozen=True, slots=True)
class TopologyDevice:
    """Describe a device displayed on the infrastructure map.

    A topology device describes the stable architectural identity of an
    equipment. Runtime health and observation data are deliberately excluded
    from this model.
    """

    device_id: str
    label: str
    kind: TopologyDeviceKind
    node_id: str | None = None
    address: str | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and normalize the topology device."""
        device_id = self.device_id.strip()
        label = self.label.strip()
        node_id = self._normalize_optional_text(self.node_id)
        address = self._normalize_optional_text(self.address)

        if not device_id:
            raise ValueError("device_id must not be empty")

        if not label:
            raise ValueError("label must not be empty")

        object.__setattr__(self, "device_id", device_id)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "node_id", node_id)
        object.__setattr__(self, "address", address)
        object.__setattr__(
            self,
            "metadata",
            freeze_mapping(self.metadata),
        )

    @staticmethod
    def _normalize_optional_text(value: str | None) -> str | None:
        """Normalize optional textual values."""
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            return None

        return normalized