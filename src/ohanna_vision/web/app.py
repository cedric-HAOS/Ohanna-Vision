"""FastAPI application factory for Ohanna-Vision."""

from pathlib import Path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

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
    websocket_hub: WebSocketHub | None = None,
) -> FastAPI:
    """Create and configure the Ohanna-Vision FastAPI application."""
    app = FastAPI(
        title=APPLICATION_NAME,
        version=APPLICATION_VERSION,
    )

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

    return app