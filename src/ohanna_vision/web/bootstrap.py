"""Application composition for Ohanna-Vision."""

from pathlib import Path

from fastapi import FastAPI

from ohanna_vision.configuration import (
    ApplicationConfiguration,
    ConfigurationLoader,
)
from ohanna_vision.domain import ObservationStore
from ohanna_vision.runtime import BackendRuntime
from ohanna_vision.timeline import TimelineEngine
from ohanna_vision.topology import (
    build_ohanna_house_topology,
)
from ohanna_vision.web.app import create_app
from ohanna_vision.web.application_context import ApplicationContext


def build_application_context() -> ApplicationContext:
    """Build the default Ohanna-Vision application context."""
    runtime = BackendRuntime()
    observation_store = ObservationStore()
    timeline_engine = TimelineEngine()

    runtime.start()

    return ApplicationContext(
        runtime=runtime,
        observation_store=observation_store,
        timeline_engine=timeline_engine,
    )


def build_application(
    *,
    configuration_path: Path | None = None,
    configuration: ApplicationConfiguration | None = None,
) -> FastAPI:
    """Build the fully configured Ohanna-Vision application."""
    if configuration is not None and configuration_path is not None:
        raise ValueError(
            "Configuration and configuration_path cannot be provided together."
        )

    if configuration is not None:
        resolved_configuration = configuration
    elif configuration_path is not None:
        resolved_configuration = ConfigurationLoader.load(configuration_path)
    else:
        resolved_configuration = ApplicationConfiguration()

    context = build_application_context()
    topology = build_ohanna_house_topology()

    return create_app(
        context=context,
        configuration=resolved_configuration,
        topology=topology,
    )


app = build_application()
