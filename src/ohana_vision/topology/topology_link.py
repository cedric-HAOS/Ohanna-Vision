"""Link represented in the Ohana-House infrastructure topology."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from math import isfinite

from ohana_vision.topology.immutable import freeze_mapping
from ohana_vision.topology.topology_link_direction import (
    TopologyLinkDirection,
)
from ohana_vision.topology.topology_link_kind import (
    TopologyLinkKind,
)


@dataclass(frozen=True, slots=True)
class TopologyLink:
    """Describe a physical or logical link between two topology devices.

    The link stores stable architectural information only. Runtime health,
    latency and availability are deliberately excluded from this model.
    """

    link_id: str
    source_device_id: str
    target_device_id: str
    kind: TopologyLinkKind
    direction: TopologyLinkDirection = TopologyLinkDirection.BIDIRECTIONAL
    label: str | None = None
    bandwidth_mbps: float | None = None
    metadata: Mapping[str, object] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate and normalize the topology link."""
        link_id = self.link_id.strip()
        source_device_id = self.source_device_id.strip()
        target_device_id = self.target_device_id.strip()
        label = self._normalize_optional_text(self.label)

        if not link_id:
            raise ValueError("link_id must not be empty")

        if not source_device_id:
            raise ValueError("source_device_id must not be empty")

        if not target_device_id:
            raise ValueError("target_device_id must not be empty")

        if source_device_id == target_device_id:
            raise ValueError("source_device_id and target_device_id must differ")

        if self.bandwidth_mbps is not None:
            if not isfinite(self.bandwidth_mbps):
                raise ValueError("bandwidth_mbps must be finite")

            if self.bandwidth_mbps <= 0:
                raise ValueError("bandwidth_mbps must be greater than zero")

        object.__setattr__(self, "link_id", link_id)
        object.__setattr__(
            self,
            "source_device_id",
            source_device_id,
        )
        object.__setattr__(
            self,
            "target_device_id",
            target_device_id,
        )
        object.__setattr__(self, "label", label)
        object.__setattr__(
            self,
            "metadata",
            freeze_mapping(self.metadata),
        )

    @staticmethod
    def _normalize_optional_text(value: str | None) -> str | None:
        """Normalize an optional textual value."""
        if value is None:
            return None

        normalized = value.strip()

        if not normalized:
            return None

        return normalized
