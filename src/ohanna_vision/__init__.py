"""Ohanna-Vision application package."""

from importlib.metadata import (
    PackageNotFoundError,
    version,
)


def get_application_version() -> str:
    """Return the installed Ohanna-Vision package version."""
    try:
        return version("ohanna-vision")
    except PackageNotFoundError:
        return "unknown"


__version__ = get_application_version()

__all__ = [
    "__version__",
    "get_application_version",
]