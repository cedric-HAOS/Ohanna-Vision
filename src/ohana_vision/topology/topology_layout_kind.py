"""Kinds of layouts supported by infrastructure topology maps."""

from enum import StrEnum


class TopologyLayoutKind(StrEnum):
    """Identify the purpose of a topology layout."""

    PHYSICAL = "physical"
    LOGICAL = "logical"
    SERVICES = "services"
    CUSTOM = "custom"
