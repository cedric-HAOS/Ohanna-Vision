"""REST request model used to ingest infrastructure snapshots."""

from __future__ import annotations

from typing import Annotated, Literal, Self

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StringConstraints,
    model_validator,
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
    tags: tuple[NonEmptyString, ...] = Field(
        default_factory=tuple,
    )

    @model_validator(mode="after")
    def validate_unique_tags(self) -> Self:
        """Require metadata tags to be unique."""
        if len(self.tags) != len(set(self.tags)):
            raise ValueError(
                "metadata tags must be unique"
            )

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
    """Infrastructure node declared by Ohanna-Agent."""

    model_config = ConfigDict(
        extra="forbid",
        frozen=True,
    )

    node_id: NonEmptyString
    name: NonEmptyString
    description: str = ""
    endpoint: InfrastructureEndpointRequest


class InfrastructureServiceRequest(BaseModel):
    """Infrastructure service declared by Ohanna-Agent."""

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

    nodes: tuple[
        InfrastructureNodeRequest,
        ...,
    ] = Field(default_factory=tuple)

    services: tuple[
        InfrastructureServiceRequest,
        ...,
    ] = Field(default_factory=tuple)

    @model_validator(mode="after")
    def validate_references(self) -> Self:
        """Validate identifiers and service references."""
        node_ids = [
            node.node_id
            for node in self.nodes
        ]

        if len(node_ids) != len(set(node_ids)):
            raise ValueError(
                "node identifiers must be unique"
            )

        service_ids = [
            service.service_id
            for service in self.services
        ]

        if len(service_ids) != len(set(service_ids)):
            raise ValueError(
                "service identifiers must be unique"
            )

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

        return self