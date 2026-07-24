"""Routers exposed by the Ohana-Vision web application."""

from ohana_vision.web.routers.api import router as api_router
from ohana_vision.web.routers.observations import (
    router as observations_router,
)
from ohana_vision.web.routers.root import router as root_router
from ohana_vision.web.routers.runtime import (
    router as runtime_router,
)
from ohana_vision.web.routers.timeline import (
    router as timeline_router,
)
from ohana_vision.web.routers.websocket import (
    router as websocket_router,
)

__all__ = [
    "api_router",
    "observations_router",
    "root_router",
    "runtime_router",
    "timeline_router",
    "websocket_router",
]
