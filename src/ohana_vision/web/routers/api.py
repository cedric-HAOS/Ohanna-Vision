"""API router for Ohana-Vision."""

from fastapi import APIRouter

from ohana_vision.web.routers.infrastructure import (
    router as infrastructure_router,
)
from ohana_vision.web.routers.observations import (
    router as observations_router,
)
from ohana_vision.web.routers.runtime import (
    router as runtime_router,
)
from ohana_vision.web.routers.timeline import (
    router as timeline_router,
)

router = APIRouter(
    prefix="/api",
    tags=["api"],
)


@router.get(
    "/",
    summary="API status",
)
def api_status() -> dict[str, str]:
    """Return the basic API status."""
    return {
        "name": "Ohana Vision API",
        "status": "running",
    }


router.include_router(runtime_router)
router.include_router(observations_router)
router.include_router(timeline_router)
router.include_router(infrastructure_router)
