"""Application configuration for Ohanna-Vision."""

from pydantic import model_validator

from ohanna_vision.configuration.base import ConfigurationModel
from ohanna_vision.configuration.environment import Environment
from ohanna_vision.configuration.server import ServerConfiguration
from ohanna_vision.configuration.web import WebConfiguration


class ApplicationConfiguration(ConfigurationModel):
    """Complete configuration of Ohanna-Vision."""

    name: str = "Ohanna Vision"
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
