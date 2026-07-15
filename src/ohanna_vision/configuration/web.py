"""Web interface configuration for Ohanna-Vision."""

from ohanna_vision.configuration.base import ConfigurationModel


class WebConfiguration(ConfigurationModel):
    """Configuration of the HTTP and documentation interfaces."""

    documentation_enabled: bool = True
