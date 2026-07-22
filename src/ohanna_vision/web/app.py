"""FastAPI application factory for Ohanna-Vision."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from ohanna_vision.configuration import (
    ApplicationConfiguration,
)
from ohanna_vision.topology import Topology
from ohanna_vision.web.api.topology_router import (
    router as topology_router,
)
from ohanna_vision.web.application_context import ApplicationContext
from ohanna_vision.web.routers import (
    api_router,
    root_router,
    websocket_router,
)
from ohanna_vision.web.websocket_hub import WebSocketHub

APPLICATION_NAME = "Ohanna Vision"
APPLICATION_VERSION = "0.1.0"

STATIC_DIRECTORY = Path(__file__).parent / "static"


def create_app(
    context: ApplicationContext | None = None,
    *,
    configuration: ApplicationConfiguration | None = None,
    websocket_hub: WebSocketHub | None = None,
    topology: Topology | None = None,
) -> FastAPI:
    """Create and configure the Ohanna-Vision application."""
    resolved_configuration = configuration or ApplicationConfiguration()

    documentation_enabled = (
        resolved_configuration.web.documentation_enabled
    )

    app = FastAPI(
        title=resolved_configuration.name,
        version=APPLICATION_VERSION,
        debug=resolved_configuration.debug,
        docs_url="/docs" if documentation_enabled else None,
        redoc_url="/redoc" if documentation_enabled else None,
        openapi_url=(
            "/openapi.json"
            if documentation_enabled
            else None
        ),
    )

    resolved_topology = topology or Topology(
        topology_id="ohanna-house",
        label="Ohanna-House",
    )

    app.state.configuration = resolved_configuration
    app.state.base_topology = resolved_topology
    app.state.topology = resolved_topology
    app.state.infrastructure_snapshot = None

    if context is not None:
        app.state.context = context

    app.state.websocket_hub = websocket_hub or WebSocketHub()

    app.include_router(root_router)
    app.include_router(api_router)
    app.include_router(websocket_router)

    app.mount(
        "/ui",
        StaticFiles(
            directory=STATIC_DIRECTORY,
            html=True,
        ),
        name="ui",
    )

    app.include_router(topology_router)

    return app