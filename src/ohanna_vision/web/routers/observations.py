"""Observation API routes for Ohanna-Vision."""

from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status

from ohanna_vision.domain.observation import Observation
from ohanna_vision.web.dependencies import ObservationStoreDependency

router = APIRouter(
    prefix="/observations",
    tags=["observations"],
)

OptionalStringQuery = Annotated[str | None, Query()]
OptionalDatetimeQuery = Annotated[datetime | None, Query()]


@router.get(
    "",
    summary="Stored observations",
)
def get_observations(
    observation_store: ObservationStoreDependency,
    node_id: OptionalStringQuery = None,
    service_id: OptionalStringQuery = None,
    capability_id: OptionalStringQuery = None,
    since: OptionalDatetimeQuery = None,
    until: OptionalDatetimeQuery = None,
) -> list[Observation]:
    """Return stored observations matching the requested filters."""
    try:
        observations = observation_store.history(
            node_id=node_id,
            service_id=service_id,
            capability_id=capability_id,
            since=since,
            until=until,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(error),
        ) from error

    return list(observations)