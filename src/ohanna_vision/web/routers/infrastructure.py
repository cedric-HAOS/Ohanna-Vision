"""Infrastructure API routes for Ohanna-Vision."""

from fastapi import APIRouter, Request, status

from ohanna_vision.web.infrastructure_ingestion_response import (
    InfrastructureIngestionResponse,
)
from ohanna_vision.web.infrastructure_request import (
    InfrastructureRequest,
)
from ohanna_vision.web.infrastructure_mapper import (
    InfrastructureMapper,
)

router = APIRouter(
    prefix="/infrastructure",
    tags=["infrastructure"],
)


@router.put(
    "",
    response_model=InfrastructureIngestionResponse,
    status_code=status.HTTP_200_OK,
)
async def ingest_infrastructure(
    request: Request,
    infrastructure_request: InfrastructureRequest,
) -> InfrastructureIngestionResponse:
    """Store and project the latest infrastructure snapshot."""
    topology = InfrastructureMapper.to_topology(
        infrastructure_request,
        base_topology=(
            request.app.state.base_topology
        ),
    )

    request.app.state.infrastructure_snapshot = (
        infrastructure_request
    )
    request.app.state.topology = topology

    await request.app.state.websocket_hub.broadcast(
        {
            "type": "infrastructure.updated",
            "infrastructure_id": (
                infrastructure_request.infrastructure_id
            ),
            "node_count": len(
                infrastructure_request.nodes
            ),
            "service_count": len(
                infrastructure_request.services
            ),
        }
    )

    return InfrastructureIngestionResponse(
        accepted=True,
        infrastructure_id=(
            infrastructure_request.infrastructure_id
        ),
        node_count=len(
            infrastructure_request.nodes
        ),
        service_count=len(
            infrastructure_request.services
        ),
    )