"""Root routes for the Ohana-Vision web application."""

from fastapi import APIRouter, status
from fastapi.responses import RedirectResponse

router = APIRouter(
    tags=["application"],
)


@router.get(
    "/",
    response_class=RedirectResponse,
    status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    summary="Open the web interface",
)
def open_web_interface() -> RedirectResponse:
    """Redirect the application root to the web interface."""
    return RedirectResponse(
        url="/ui/",
        status_code=status.HTTP_307_TEMPORARY_REDIRECT,
    )
