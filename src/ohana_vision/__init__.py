"""Ohana-Vision application package."""

from importlib.metadata import (
    PackageNotFoundError,
    version,
)


def get_application_version() -> str:
    """Return the installed Ohana-Vision package version."""
    try:
        return version("ohana-vision")
    except PackageNotFoundError:
        return "unknown"


__version__ = get_application_version()

__all__ = [
    "__version__",
    "get_application_version",
]
