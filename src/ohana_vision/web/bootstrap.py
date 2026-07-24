"""Application composition for Ohana-Vision."""

from pathlib import Path

from fastapi import FastAPI

from ohana_vision.administration import AgentAdministrationClient
from ohana_vision.configuration import (
    ApplicationConfiguration,
    ConfigurationLoader,
)
from ohana_vision.domain import ObservationStore
from ohana_vision.runtime import BackendRuntime
from ohana_vision.timeline import TimelineEngine
from ohana_vision.web.app import create_app
from ohana_vision.web.application_context import ApplicationContext


def build_application_context() -> ApplicationContext:
    """Build the default Ohana-Vision application context."""
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
    """Build the fully configured Ohana-Vision application."""
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
    administration_client = None

    if resolved_configuration.agent.administration_enabled:
        administration_client = AgentAdministrationClient(
            base_url=str(
                resolved_configuration.agent.administration_url
            ),
            token_file=resolved_configuration.agent.token_file,
            timeout_seconds=(
                resolved_configuration.agent.timeout_seconds
            ),
        )

    return create_app(
        context=context,
        configuration=resolved_configuration,
        administration_client=administration_client,
    )


app = build_application()
