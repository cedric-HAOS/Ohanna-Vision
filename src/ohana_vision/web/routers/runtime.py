"""Runtime API routes for Ohana-Vision."""

from fastapi import APIRouter

from ohana_vision.runtime import RuntimeSnapshot
from ohana_vision.web.dependencies import (
    RuntimeDependency,
)

router = APIRouter(
    prefix="/runtime",
    tags=["runtime"],
)


@router.get(
    "",
    summary="Runtime snapshot",
)
def get_runtime_snapshot(
    runtime: RuntimeDependency,
) -> RuntimeSnapshot:
    """Return the current backend runtime snapshot."""
    return runtime.snapshot()
