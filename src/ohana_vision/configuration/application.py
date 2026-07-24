"""Application configuration for Ohana-Vision."""

from pydantic import model_validator

from ohana_vision.configuration.base import ConfigurationModel
from ohana_vision.configuration.environment import Environment
from ohana_vision.configuration.server import ServerConfiguration
from ohana_vision.configuration.web import WebConfiguration


class ApplicationConfiguration(ConfigurationModel):
    """Complete configuration of Ohana-Vision."""

    name: str = "Ohana Vision"
    environment: Environment = Environment.DEVELOPMENT
    debug: bool = False
    server: ServerConfiguration = ServerConfiguration()
    web: WebConfiguration = WebConfiguration()

    @model_validator(mode="after")
    def validate_production_configuration(
        self,
    ) -> "ApplicationConfiguration":
        """Reject unsafe development settings in production."""
        if self.environment is Environment.PRODUCTION and self.debug:
            raise ValueError("Debug mode cannot be enabled in production.")

        return self
