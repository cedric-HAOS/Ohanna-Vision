"""REST request model used to ingest infrastructure snapshots."""

from __future__ import annotations

from typing import Annotated, Any, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
)

from ohana_vision.topology import (
    TopologyDeviceKind,
    TopologyLayoutKind,
    TopologyLinkDirection,
    TopologyLinkKind,
)

NonEmptyString = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=1,
    ),
]


class InfrastructureMetadataRequest(BaseModel):
    """Metadata attached to an infrastructure snapshot."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    version: NonEmptyString = "1.0"
    tags: tuple[NonEmptyString, ...] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def validate_unique_tags(self) -> Self:
        """Require metadata tags to be unique."""
        if len(self.tags) != len(set(self.tags)):
            raise ValueError("metadata tags must be unique")

        return self


class InfrastructureEndpointRequest(BaseModel):
    """Network endpoint associated with one node."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    type: NonEmptyString
    address: NonEmptyString


class InfrastructureNodeRequest(BaseModel):
    """Infrastructure node declared by Ohana-Agent."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    node_id: NonEmptyString
    name: NonEmptyString
    description: str = ""
    endpoint: InfrastructureEndpointRequest


class InfrastructureServiceRequest(BaseModel):
    """Infrastructure service declared by Ohana-Agent."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    service_id: NonEmptyString
    name: NonEmptyString
    type: NonEmptyString
    node_id: NonEmptyString
    port: int | None = Field(
        default=None,
        ge=1,
        le=65535,
    )


class InfrastructureTopologyDeviceRequest(BaseModel):
    """Device displayed in a topology supplied by Ohana-Agent."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    device_id: NonEmptyString
    label: NonEmptyString
    kind: TopologyDeviceKind
    node_id: NonEmptyString | None = None
    address: NonEmptyString | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)


class InfrastructureTopologyLinkRequest(BaseModel):
    """Link displayed in a topology supplied by Ohana-Agent."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    link_id: NonEmptyString
    source_device_id: NonEmptyString
    target_device_id: NonEmptyString
    kind: TopologyLinkKind
    direction: TopologyLinkDirection = TopologyLinkDirection.BIDIRECTIONAL
    label: NonEmptyString | None = None
    bandwidth_mbps: float | None = Field(
        default=None,
        gt=0,
        allow_inf_nan=False,
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_distinct_devices(self) -> Self:
        """Require links to connect two distinct devices."""
        if self.source_device_id == self.target_device_id:
            raise ValueError(
                "source_device_id and target_device_id must differ"
            )

        return self


class InfrastructureGridPositionRequest(BaseModel):
    """Logical grid cell supplied for one topology device."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    column: int = Field(ge=0)
    row: int = Field(ge=0)


class InfrastructureTopologyLayoutRequest(BaseModel):
    """Logical layout supplied by Ohana-Agent."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    layout_id: NonEmptyString
    label: NonEmptyString
    kind: TopologyLayoutKind
    positions: dict[NonEmptyString, InfrastructureGridPositionRequest] = Field(
        default_factory=dict
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_unique_grid_cells(self) -> Self:
        """Require one device at most in each logical grid cell."""
        grid_cells = [
            (position.column, position.row)
            for position in self.positions.values()
        ]

        if len(grid_cells) != len(set(grid_cells)):
            raise ValueError("layout grid positions must be unique")

        return self


class InfrastructureTopologyRequest(BaseModel):
    """Complete topology definition supplied by Ohana-Agent."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    devices: tuple[InfrastructureTopologyDeviceRequest, ...] = Field(
        default_factory=tuple
    )
    links: tuple[InfrastructureTopologyLinkRequest, ...] = Field(
        default_factory=tuple
    )
    layouts: tuple[InfrastructureTopologyLayoutRequest, ...] = Field(
        default_factory=tuple
    )
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="after")
    def validate_topology_references(self) -> Self:
        """Validate topology identifiers and internal references."""
        device_ids = [device.device_id for device in self.devices]

        if len(device_ids) != len(set(device_ids)):
            raise ValueError("topology device identifiers must be unique")

        known_device_ids = set(device_ids)
        link_ids = [link.link_id for link in self.links]

        if len(link_ids) != len(set(link_ids)):
            raise ValueError("topology link identifiers must be unique")

        for link in self.links:
            unknown_device_ids = sorted(
                {
                    link.source_device_id,
                    link.target_device_id,
                }
                - known_device_ids
            )

            if unknown_device_ids:
                unknown = ", ".join(unknown_device_ids)
                raise ValueError(
                    f"topology links reference unknown devices: {unknown}"
                )

        layout_ids = [layout.layout_id for layout in self.layouts]

        if len(layout_ids) != len(set(layout_ids)):
            raise ValueError("topology layout identifiers must be unique")

        for layout in self.layouts:
            unknown_device_ids = sorted(
                set(layout.positions) - known_device_ids
            )

            if unknown_device_ids:
                unknown = ", ".join(unknown_device_ids)
                raise ValueError(
                    "topology layouts reference unknown devices: "
                    f"{unknown}"
                )

        return self


class InfrastructureRequest(BaseModel):
    """Complete infrastructure snapshot received from Agent."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    schema_version: Literal[1]

    infrastructure_id: NonEmptyString
    name: NonEmptyString
    environment: NonEmptyString

    metadata: InfrastructureMetadataRequest = Field(
        default_factory=InfrastructureMetadataRequest,
    )
    nodes: tuple[InfrastructureNodeRequest, ...] = Field(default_factory=tuple)
    services: tuple[InfrastructureServiceRequest, ...] = Field(
        default_factory=tuple
    )
    topology: InfrastructureTopologyRequest | None = None

    @model_validator(mode="after")
    def validate_references(self) -> Self:
        """Validate identifiers and cross-section references."""
        node_ids = [node.node_id for node in self.nodes]

        if len(node_ids) != len(set(node_ids)):
            raise ValueError("node identifiers must be unique")

        service_ids = [service.service_id for service in self.services]

        if len(service_ids) != len(set(service_ids)):
            raise ValueError("service identifiers must be unique")

        known_node_ids = set(node_ids)
        unknown_node_ids = sorted(
            {
                service.node_id
                for service in self.services
                if service.node_id not in known_node_ids
            }
        )

        if unknown_node_ids:
            unknown = ", ".join(unknown_node_ids)
            raise ValueError(
                "services reference unknown node identifiers: "
                f"{unknown}"
            )

        if self.topology is None:
            return self

        topology_node_ids = [
            device.node_id
            for device in self.topology.devices
            if device.node_id is not None
        ]

        unknown_topology_node_ids = sorted(
            set(topology_node_ids) - known_node_ids
        )

        if unknown_topology_node_ids:
            unknown = ", ".join(unknown_topology_node_ids)
            raise ValueError(
                "topology devices reference unknown node identifiers: "
                f"{unknown}"
            )

        if len(topology_node_ids) != len(set(topology_node_ids)):
            raise ValueError("topology node references must be unique")

        return self
