"""Root routes for the Ohana-Vision web application."""

from fastapi import APIRouter

APPLICATION_NAME = "Ohana Vision"

router = APIRouter(
    tags=["application"],
)


@router.get(
    "/",
    summary="Application status",
)
def application_status() -> dict[str, str]:
    """Return the basic application status."""
    return {
        "name": APPLICATION_NAME,
        "status": "running",
    }
