"""HTTP routes exposing infrastructure topology data."""

from typing import Annotated

from fastapi import APIRouter, Depends

from ohana_vision.topology import Topology
from ohana_vision.web.api.topology_mapper import (
    topology_to_response,
)
from ohana_vision.web.api.topology_schemas import (
    TopologyResponse,
)
from ohana_vision.web.dependencies import get_topology

router = APIRouter(
    prefix="/api",
    tags=["topology"],
)


@router.get(
    "/topology",
    response_model=TopologyResponse,
)
def read_topology(
    topology: Annotated[
        Topology,
        Depends(get_topology),
    ],
) -> TopologyResponse:
    """Return the complete configured infrastructure topology."""
    return topology_to_response(topology)
