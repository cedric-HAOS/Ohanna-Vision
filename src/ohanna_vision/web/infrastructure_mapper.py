"""Mapping between infrastructure requests and topology domain models."""

from __future__ import annotations

from collections.abc import Iterable

from ohanna_vision.topology import (
    Topology,
    TopologyDevice,
    TopologyDeviceKind,
    TopologyLayout,
    TopologyLayoutKind,
    TopologyPosition,
)
from ohanna_vision.web.infrastructure_request import (
    InfrastructureNodeRequest,
    InfrastructureRequest,
    InfrastructureServiceRequest,
)

_LAYOUT_MARGIN_X = 150.0
_LAYOUT_MARGIN_Y = 150.0
_LAYOUT_COLUMN_SPACING = 300.0
_LAYOUT_ROW_SPACING = 260.0
_LAYOUT_COLUMN_COUNT = 5


class InfrastructureMapper:
    """Project an Agent infrastructure snapshot into a Vision topology."""

    @classmethod
    def to_topology(
        cls,
        request: InfrastructureRequest,
        *,
        base_topology: Topology | None = None,
    ) -> Topology:
        """Reconcile an Agent snapshot with a presentation topology."""
        resolved_base = base_topology or Topology(
            topology_id=request.infrastructure_id,
            label=request.name,
        )

        services_by_node = cls._index_services(
            request.services
        )
        nodes_by_id = {
            node.node_id: node
            for node in request.nodes
        }

        projected_devices: list[TopologyDevice] = []
        matched_node_ids: set[str] = set()

        for device in resolved_base.devices:
            node = cls._find_matching_node(
                device=device,
                nodes_by_id=nodes_by_id,
            )

            if node is None:
                projected_devices.append(device)
                continue

            matched_node_ids.add(node.node_id)

            projected_devices.append(
                cls._enrich_device(
                    device=device,
                    node=node,
                    services=services_by_node.get(
                        node.node_id,
                        (),
                    ),
                )
            )

        added_device_ids: list[str] = []

        for node in request.nodes:
            if node.node_id in matched_node_ids:
                continue

            projected_devices.append(
                cls._build_device(
                    node=node,
                    services=services_by_node.get(
                        node.node_id,
                        (),
                    ),
                )
            )
            added_device_ids.append(node.node_id)

        projected_layouts = cls._project_layouts(
            layouts=resolved_base.layouts,
            device_ids=tuple(
                device.device_id
                for device in projected_devices
            ),
            added_device_ids=tuple(added_device_ids),
            infrastructure_id=request.infrastructure_id,
            infrastructure_name=request.name,
        )

        metadata = dict(resolved_base.metadata)
        metadata.update(
            {
                "source": "ohanna-agent",
                "schema_version": request.schema_version,
                "environment": request.environment,
                "configuration_version": (
                    request.metadata.version
                ),
                "tags": request.metadata.tags,
                "service_count": len(request.services),
            }
        )

        return Topology(
            topology_id=request.infrastructure_id,
            label=request.name,
            devices=tuple(projected_devices),
            links=resolved_base.links,
            layouts=projected_layouts,
            metadata=metadata,
        )

    @staticmethod
    def _index_services(
        services: Iterable[
            InfrastructureServiceRequest
        ],
    ) -> dict[
        str,
        tuple[InfrastructureServiceRequest, ...],
    ]:
        """Group services by their owning node."""
        indexed: dict[
            str,
            list[InfrastructureServiceRequest],
        ] = {}

        for service in services:
            indexed.setdefault(
                service.node_id,
                [],
            ).append(service)

        return {
            node_id: tuple(node_services)
            for node_id, node_services
            in indexed.items()
        }

    @staticmethod
    def _find_matching_node(
        *,
        device: TopologyDevice,
        nodes_by_id: dict[
            str,
            InfrastructureNodeRequest,
        ],
    ) -> InfrastructureNodeRequest | None:
        """Find the Agent node represented by a device."""
        if device.node_id is not None:
            node = nodes_by_id.get(device.node_id)

            if node is not None:
                return node

        return nodes_by_id.get(device.device_id)

    @classmethod
    def _enrich_device(
        cls,
        *,
        device: TopologyDevice,
        node: InfrastructureNodeRequest,
        services: tuple[
            InfrastructureServiceRequest,
            ...,
        ],
    ) -> TopologyDevice:
        """Enrich an existing device with Agent data."""
        metadata = dict(device.metadata)
        metadata.update(
            cls._node_metadata(
                node,
                services,
            )
        )

        return TopologyDevice(
            device_id=device.device_id,
            label=node.name,
            kind=device.kind,
            node_id=node.node_id,
            address=node.endpoint.address,
            metadata=metadata,
        )

    @classmethod
    def _build_device(
        cls,
        *,
        node: InfrastructureNodeRequest,
        services: tuple[
            InfrastructureServiceRequest,
            ...,
        ],
    ) -> TopologyDevice:
        """Build a generic device for a newly declared node."""
        metadata = {
            "role": "managed_node",
            **cls._node_metadata(
                node,
                services,
            ),
        }

        return TopologyDevice(
            device_id=node.node_id,
            label=node.name,
            kind=TopologyDeviceKind.SERVER,
            node_id=node.node_id,
            address=node.endpoint.address,
            metadata=metadata,
        )

    @staticmethod
    def _node_metadata(
        node: InfrastructureNodeRequest,
        services: tuple[
            InfrastructureServiceRequest,
            ...,
        ],
    ) -> dict[str, object]:
        """Build topology metadata from one Agent node."""
        return {
            "source": "ohanna-agent",
            "description": node.description,
            "endpoint_type": node.endpoint.type,
            "services": tuple(
                {
                    "service_id": service.service_id,
                    "name": service.name,
                    "type": service.type,
                    "port": service.port,
                }
                for service in services
            ),
        }

    @classmethod
    def _project_layouts(
        cls,
        *,
        layouts: tuple[TopologyLayout, ...],
        device_ids: tuple[str, ...],
        added_device_ids: tuple[str, ...],
        infrastructure_id: str,
        infrastructure_name: str,
    ) -> tuple[TopologyLayout, ...]:
        """Preserve layouts and position newly declared devices."""
        if not device_ids:
            return ()

        if not layouts:
            return (
                cls._build_generated_layout(
                    device_ids=device_ids,
                    infrastructure_id=(
                        infrastructure_id
                    ),
                    infrastructure_name=(
                        infrastructure_name
                    ),
                ),
            )

        return tuple(
            cls._extend_layout(
                layout=layout,
                added_device_ids=added_device_ids,
            )
            for layout in layouts
        )

    @classmethod
    def _build_generated_layout(
        cls,
        *,
        device_ids: tuple[str, ...],
        infrastructure_id: str,
        infrastructure_name: str,
    ) -> TopologyLayout:
        """Build a logical layout when no profile exists."""
        positions = {
            device_id: cls._grid_position(index)
            for index, device_id
            in enumerate(device_ids)
        }

        row_count = cls._row_count(
            len(device_ids)
        )

        return TopologyLayout(
            layout_id=(
                f"{infrastructure_id}-logical"
            ),
            label=(
                f"Infrastructure "
                f"{infrastructure_name}"
            ),
            kind=TopologyLayoutKind.LOGICAL,
            positions=positions,
            canvas_width=cls._canvas_width(
                len(device_ids)
            ),
            canvas_height=cls._canvas_height(
                row_count
            ),
            metadata={
                "source": "ohanna-agent",
                "generated": True,
            },
        )

    @classmethod
    def _extend_layout(
        cls,
        *,
        layout: TopologyLayout,
        added_device_ids: tuple[str, ...],
    ) -> TopologyLayout:
        """Position devices absent from an existing layout."""
        if not added_device_ids:
            return layout

        positions = dict(layout.positions)

        maximum_y = max(
            (
                position.y
                for position in positions.values()
            ),
            default=(
                _LAYOUT_MARGIN_Y
                - _LAYOUT_ROW_SPACING
            ),
        )

        first_row_y = (
            maximum_y
            + _LAYOUT_ROW_SPACING
        )

        for index, device_id in enumerate(
            added_device_ids
        ):
            column = (
                index
                % _LAYOUT_COLUMN_COUNT
            )
            row = (
                index
                // _LAYOUT_COLUMN_COUNT
            )

            positions[device_id] = (
                TopologyPosition(
                    x=(
                        _LAYOUT_MARGIN_X
                        + column
                        * _LAYOUT_COLUMN_SPACING
                    ),
                    y=(
                        first_row_y
                        + row
                        * _LAYOUT_ROW_SPACING
                    ),
                    layer=row,
                    pinned=True,
                )
            )

        added_row_count = cls._row_count(
            len(added_device_ids)
        )

        required_height = (
            first_row_y
            + (
                added_row_count - 1
            )
            * _LAYOUT_ROW_SPACING
            + _LAYOUT_MARGIN_Y
        )

        return TopologyLayout(
            layout_id=layout.layout_id,
            label=layout.label,
            kind=layout.kind,
            positions=positions,
            canvas_width=max(
                layout.canvas_width,
                cls._canvas_width(
                    len(added_device_ids)
                ),
            ),
            canvas_height=max(
                layout.canvas_height,
                required_height,
            ),
            metadata=layout.metadata,
        )

    @staticmethod
    def _grid_position(
        index: int,
    ) -> TopologyPosition:
        """Return a deterministic grid position."""
        column = (
            index
            % _LAYOUT_COLUMN_COUNT
        )
        row = (
            index
            // _LAYOUT_COLUMN_COUNT
        )

        return TopologyPosition(
            x=(
                _LAYOUT_MARGIN_X
                + column
                * _LAYOUT_COLUMN_SPACING
            ),
            y=(
                _LAYOUT_MARGIN_Y
                + row
                * _LAYOUT_ROW_SPACING
            ),
            layer=row,
            pinned=True,
        )

    @staticmethod
    def _row_count(
        device_count: int,
    ) -> int:
        """Return the required row count."""
        return max(
            1,
            (
                device_count
                + _LAYOUT_COLUMN_COUNT
                - 1
            )
            // _LAYOUT_COLUMN_COUNT,
        )

    @staticmethod
    def _canvas_width(
        device_count: int,
    ) -> float:
        """Return the generated canvas width."""
        column_count = min(
            max(device_count, 1),
            _LAYOUT_COLUMN_COUNT,
        )

        return (
            2 * _LAYOUT_MARGIN_X
            + (
                column_count - 1
            )
            * _LAYOUT_COLUMN_SPACING
        )

    @staticmethod
    def _canvas_height(
        row_count: int,
    ) -> float:
        """Return the generated canvas height."""
        return (
            2 * _LAYOUT_MARGIN_Y
            + (
                row_count - 1
            )
            * _LAYOUT_ROW_SPACING
        )