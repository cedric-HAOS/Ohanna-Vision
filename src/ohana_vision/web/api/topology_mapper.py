"""Mapping between topology domain models and API schemas."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ohana_vision.topology import (
    Topology,
    TopologyDevice,
    TopologyLayout,
    TopologyLink,
    TopologyPosition,
)
from ohana_vision.web.api.topology_schemas import (
    TopologyDeviceResponse,
    TopologyLayoutResponse,
    TopologyLinkResponse,
    TopologyPositionResponse,
    TopologyResponse,
)


def topology_to_response(
    topology: Topology,
) -> TopologyResponse:
    """Convert a complete topology into its API representation."""
    return TopologyResponse(
        topology_id=topology.topology_id,
        label=topology.label,
        devices=[topology_device_to_response(device) for device in topology.devices],
        links=[topology_link_to_response(link) for link in topology.links],
        layouts=[topology_layout_to_response(layout) for layout in topology.layouts],
        metadata=thaw_mapping(topology.metadata),
    )


def topology_device_to_response(
    device: TopologyDevice,
) -> TopologyDeviceResponse:
    """Convert a topology device into its API representation."""
    return TopologyDeviceResponse(
        device_id=device.device_id,
        label=device.label,
        kind=device.kind.value,
        node_id=device.node_id,
        address=device.address,
        metadata=thaw_mapping(device.metadata),
    )


def topology_link_to_response(
    link: TopologyLink,
) -> TopologyLinkResponse:
    """Convert a topology link into its API representation."""
    return TopologyLinkResponse(
        link_id=link.link_id,
        source_device_id=link.source_device_id,
        target_device_id=link.target_device_id,
        kind=link.kind.value,
        direction=link.direction.value,
        label=link.label,
        bandwidth_mbps=link.bandwidth_mbps,
        metadata=thaw_mapping(link.metadata),
    )


def topology_layout_to_response(
    layout: TopologyLayout,
) -> TopologyLayoutResponse:
    """Convert a topology layout into its API representation."""
    return TopologyLayoutResponse(
        layout_id=layout.layout_id,
        label=layout.label,
        kind=layout.kind.value,
        canvas_width=layout.canvas_width,
        canvas_height=layout.canvas_height,
        positions={
            device_id: topology_position_to_response(position)
            for device_id, position in layout.positions.items()
        },
        metadata=thaw_mapping(layout.metadata),
    )


def topology_position_to_response(
    position: TopologyPosition,
) -> TopologyPositionResponse:
    """Convert a topology position into its API representation."""
    return TopologyPositionResponse(
        x=position.x,
        y=position.y,
        layer=position.layer,
        pinned=position.pinned,
    )


def thaw_mapping(
    mapping: Mapping[str, object],
) -> dict[str, Any]:
    """Convert deeply immutable domain metadata to JSON-compatible data."""
    return {key: thaw_value(value) for key, value in mapping.items()}


def thaw_value(value: object) -> Any:
    """Recursively convert immutable domain values to mutable JSON values."""
    if isinstance(value, Mapping):
        return {key: thaw_value(nested_value) for key, nested_value in value.items()}

    if isinstance(value, tuple | list):
        return [thaw_value(item) for item in value]

    if isinstance(value, frozenset | set):
        return [thaw_value(item) for item in value]

    return value
