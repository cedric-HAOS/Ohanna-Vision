"""Base configuration model for Ohana-Vision."""

from pydantic import BaseModel, ConfigDict


class ConfigurationModel(BaseModel):
    """Base class shared by configuration sections."""

    model_config = ConfigDict(
        frozen=True,
        extra="forbid",
    )
