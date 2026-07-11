"""Runtime API routes for Ohanna-Vision."""

from fastapi import APIRouter

from ohanna_vision.runtime import RuntimeSnapshot
from ohanna_vision.web.dependencies import RuntimeDependency

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