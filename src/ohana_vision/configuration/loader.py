"""YAML configuration loader for Ohana-Vision."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from ohana_vision.configuration.application import (
    ApplicationConfiguration,
)


class ConfigurationError(ValueError):
    """Raised when an application configuration cannot be loaded."""


class ConfigurationLoader:
    """Load and validate an Ohana-Vision YAML configuration."""

    @classmethod
    def load(
        cls,
        path: Path,
    ) -> ApplicationConfiguration:
        """Load an application configuration from a YAML file."""
        if not path.is_file():
            raise ConfigurationError(f"Configuration file does not exist: {path}")

        try:
            payload = cls._read_yaml(path)
            return ApplicationConfiguration.model_validate(payload)
        except yaml.YAMLError as error:
            raise ConfigurationError(f"Invalid YAML configuration: {path}") from error
        except ValidationError as error:
            raise ConfigurationError(
                f"Invalid application configuration: {path}"
            ) from error

    @staticmethod
    def _read_yaml(path: Path) -> dict[str, Any]:
        """Read the YAML payload stored at the supplied path."""
        with path.open(
            mode="r",
            encoding="utf-8",
        ) as configuration_file:
            payload = yaml.safe_load(configuration_file)

        if payload is None:
            return {}

        if not isinstance(payload, dict):
            raise ConfigurationError(
                "The application configuration root must be a mapping."
            )

        return payload
