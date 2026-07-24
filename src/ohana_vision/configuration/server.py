"""HTTP server configuration for Ohana-Vision."""

from pydantic import Field

from ohana_vision.configuration.base import ConfigurationModel


class ServerConfiguration(ConfigurationModel):
    """Configuration of the HTTP application server."""

    host: str = "127.0.0.1"
    port: int = Field(
        default=8000,
        ge=1,
        le=65535,
    )
    log_level: str = "info"
