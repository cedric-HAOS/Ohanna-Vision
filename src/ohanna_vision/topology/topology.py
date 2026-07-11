"""Aggregate representing an infrastructure topology."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from ohanna_vision.topology.immutable import freeze_mapping
from ohanna_vision.topology.topology_device import TopologyDevice
from ohanna_vision.topology.topology_layout import TopologyLayout
from ohanna_vision.topology.topology_link import TopologyLink


@dataclass(frozen=True, slots=True)
class Topology:
    """Describe a complete and coherent infrastructure topology.

    The aggregate owns devices, links and layouts. It guarantees that every
    relationship references existing devices and that identifiers remain
    unique within their respective collections.
    """

    topology_id: str
    label: str
    devices: tuple[TopologyDevice, ...] = ()
    links: tuple[TopologyLink, ...] = ()
    layouts: tuple[TopologyLayout, ...] = ()
    metadata: Mapping[str, object] = field(default_factory=dict)
    
    _device_index: Mapping[str, TopologyDevice] = field(
        init=False,
        repr=False,
        compare=False,
    )
    _link_index: Mapping[str, TopologyLink] = field(
        init=False,
        repr=False,
        compare=False,
    )
    _layout_index: Mapping[str, TopologyLayout] = field(
        init=False,
        repr=False,
        compare=False,
    )

    def __post_init__(self) -> None:
        """Validate and normalize the complete topology."""
        topology_id = self.topology_id.strip()
        label = self.label.strip()

        if not topology_id:
            raise ValueError("topology_id must not be empty")

        if not label:
            raise ValueError("label must not be empty")

        devices = tuple(self.devices)
        links = tuple(self.links)
        layouts = tuple(self.layouts)

        device_index = self._index_devices(devices)
        link_index = self._index_links(links)
        layout_index = self._index_layouts(layouts)

        self._validate_link_references(
            links=links,
            device_index=device_index,
        )
        self._validate_layout_references(
            layouts=layouts,
            device_index=device_index,
        )

        object.__setattr__(self, "topology_id", topology_id)
        object.__setattr__(self, "label", label)
        object.__setattr__(self, "devices", devices)
        object.__setattr__(self, "links", links)
        object.__setattr__(self, "layouts", layouts)
        object.__setattr__(
            self,
            "metadata",
            freeze_mapping(self.metadata),
        )

        object.__setattr__(
            self,
            "_device_index",
            MappingProxyType(device_index),
        )
        object.__setattr__(
            self,
            "_link_index",
            MappingProxyType(link_index),
        )
        object.__setattr__(
            self,
            "_layout_index",
            MappingProxyType(layout_index),
        )

    @property
    def device_count(self) -> int:
        """Return the number of topology devices."""
        return len(self.devices)

    @property
    def link_count(self) -> int:
        """Return the number of topology links."""
        return len(self.links)

    @property
    def layout_count(self) -> int:
        """Return the number of topology layouts."""
        return len(self.layouts)

    def device(
        self,
        device_id: str,
    ) -> TopologyDevice | None:
        """Return a topology device by identifier."""
        normalized_device_id = device_id.strip()

        if not normalized_device_id:
            return None

        return self._device_index.get(normalized_device_id)

    def link(
        self,
        link_id: str,
    ) -> TopologyLink | None:
        """Return a topology link by identifier."""
        normalized_link_id = link_id.strip()

        if not normalized_link_id:
            return None

        return self._link_index.get(normalized_link_id)

    def layout(
        self,
        layout_id: str,
    ) -> TopologyLayout | None:
        """Return a topology layout by identifier."""
        normalized_layout_id = layout_id.strip()

        if not normalized_layout_id:
            return None

        return self._layout_index.get(normalized_layout_id)

    def contains_device(self, device_id: str) -> bool:
        """Return whether the topology contains a device."""
        return self.device(device_id) is not None

    def contains_link(self, link_id: str) -> bool:
        """Return whether the topology contains a link."""
        return self.link(link_id) is not None

    def contains_layout(self, layout_id: str) -> bool:
        """Return whether the topology contains a layout."""
        return self.layout(layout_id) is not None

    def links_for_device(
        self,
        device_id: str,
    ) -> tuple[TopologyLink, ...]:
        """Return every link connected to a topology device."""
        normalized_device_id = device_id.strip()

        if not normalized_device_id:
            return ()

        return tuple(
            link
            for link in self.links
            if (
                link.source_device_id == normalized_device_id
                or link.target_device_id == normalized_device_id
            )
        )

    def outgoing_links(
        self,
        device_id: str,
    ) -> tuple[TopologyLink, ...]:
        """Return links whose source is the requested device."""
        normalized_device_id = device_id.strip()

        if not normalized_device_id:
            return ()

        return tuple(
            link
            for link in self.links
            if link.source_device_id == normalized_device_id
        )

    def incoming_links(
        self,
        device_id: str,
    ) -> tuple[TopologyLink, ...]:
        """Return links whose target is the requested device."""
        normalized_device_id = device_id.strip()

        if not normalized_device_id:
            return ()

        return tuple(
            link
            for link in self.links
            if link.target_device_id == normalized_device_id
        )

    def neighbor_devices(
        self,
        device_id: str,
    ) -> tuple[TopologyDevice, ...]:
        """Return devices directly connected to the requested device."""
        normalized_device_id = device_id.strip()

        if not normalized_device_id:
            return ()

        neighbor_ids: list[str] = []

        for link in self.links_for_device(normalized_device_id):
            if link.source_device_id == normalized_device_id:
                neighbor_id = link.target_device_id
            else:
                neighbor_id = link.source_device_id

            if neighbor_id not in neighbor_ids:
                neighbor_ids.append(neighbor_id)

        return tuple(
            device
            for neighbor_id in neighbor_ids
            if (device := self.device(neighbor_id)) is not None
        )

    @staticmethod
    def _index_devices(
        devices: tuple[TopologyDevice, ...],
    ) -> dict[str, TopologyDevice]:
        """Create the device index and reject duplicate identifiers."""
        index: dict[str, TopologyDevice] = {}

        for device in devices:
            if device.device_id in index:
                raise ValueError(
                    "device identifiers must be unique"
                )

            index[device.device_id] = device

        return index

    @staticmethod
    def _index_links(
        links: tuple[TopologyLink, ...],
    ) -> dict[str, TopologyLink]:
        """Create the link index and reject duplicate identifiers."""
        index: dict[str, TopologyLink] = {}

        for link in links:
            if link.link_id in index:
                raise ValueError(
                    "link identifiers must be unique"
                )

            index[link.link_id] = link

        return index

    @staticmethod
    def _index_layouts(
        layouts: tuple[TopologyLayout, ...],
    ) -> dict[str, TopologyLayout]:
        """Create the layout index and reject duplicate identifiers."""
        index: dict[str, TopologyLayout] = {}

        for layout in layouts:
            if layout.layout_id in index:
                raise ValueError(
                    "layout identifiers must be unique"
                )

            index[layout.layout_id] = layout

        return index

    @staticmethod
    def _validate_link_references(
        *,
        links: tuple[TopologyLink, ...],
        device_index: Mapping[str, TopologyDevice],
    ) -> None:
        """Ensure every link references existing devices."""
        for link in links:
            if link.source_device_id not in device_index:
                raise ValueError(
                    "link source device does not exist: "
                    f"{link.source_device_id}"
                )

            if link.target_device_id not in device_index:
                raise ValueError(
                    "link target device does not exist: "
                    f"{link.target_device_id}"
                )

    @staticmethod
    def _validate_layout_references(
        *,
        layouts: tuple[TopologyLayout, ...],
        device_index: Mapping[str, TopologyDevice],
    ) -> None:
        """Ensure every layout position references an existing device."""
        for layout in layouts:
            for device_id in layout.positions:
                if device_id not in device_index:
                    raise ValueError(
                        "layout position device does not exist: "
                        f"{device_id}"
                    )