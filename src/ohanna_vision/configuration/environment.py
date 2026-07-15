"""Execution environments supported by Ohanna-Vision."""

from enum import StrEnum


class Environment(StrEnum):
    """Execution environment of the application."""

    DEVELOPMENT = "development"
    TEST = "test"
    PRODUCTION = "production"
