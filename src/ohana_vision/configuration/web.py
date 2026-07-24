"""Web interface configuration for Ohana-Vision."""

from ohana_vision.configuration.base import ConfigurationModel


class WebConfiguration(ConfigurationModel):
    """Configuration of the HTTP and documentation interfaces."""

    documentation_enabled: bool = True
