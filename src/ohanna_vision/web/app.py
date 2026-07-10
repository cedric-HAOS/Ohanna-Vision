"""FastAPI application factory for Ohanna-Vision."""

from fastapi import FastAPI

APPLICATION_NAME = "Ohanna Vision"
APPLICATION_VERSION = "0.1.0"


def create_app() -> FastAPI:
    """Create and configure the Ohanna-Vision FastAPI application."""
    app = FastAPI(
        title=APPLICATION_NAME,
        version=APPLICATION_VERSION,
    )

    @app.get(
        "/",
        tags=["application"],
        summary="Application status",
    )
    def application_status() -> dict[str, str]:
        """Return the basic application status."""
        return {
            "name": APPLICATION_NAME,
            "status": "running",
        }

    return app