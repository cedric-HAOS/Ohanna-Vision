"""API schemas for infrastructure topologies."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict


class TopologyDeviceResponse(BaseModel):
    """Device exposed by the topology API."""

    model_config = ConfigDict(frozen=True)

    device_id: str
    label: str
    kind: str
    node_id: str | None
    address: str | None
    metadata: dict[str, Any]


class TopologyLinkResponse(BaseModel):
    """Link exposed by the topology API."""

    model_config = ConfigDict(frozen=True)

    link_id: str
    source_device_id: str
    target_device_id: str
    kind: str
    direction: str
    label: str | None
    bandwidth_mbps: float | None
    metadata: dict[str, Any]


class TopologyPositionResponse(BaseModel):
    """Device position exposed by the topology API."""

    model_config = ConfigDict(frozen=True)

    x: float
    y: float
    layer: int
    pinned: bool


class TopologyLayoutResponse(BaseModel):
    """Layout exposed by the topology API."""

    model_config = ConfigDict(frozen=True)

    layout_id: str
    label: str
    kind: str
    canvas_width: float
    canvas_height: float
    positions: dict[str, TopologyPositionResponse]
    metadata: dict[str, Any]


class TopologyResponse(BaseModel):
    """Complete infrastructure topology API response."""

    model_config = ConfigDict(frozen=True)

    topology_id: str
    label: str
    devices: list[TopologyDeviceResponse]
    links: list[TopologyLinkResponse]
    layouts: list[TopologyLayoutResponse]
    metadata: dict[str, Any]