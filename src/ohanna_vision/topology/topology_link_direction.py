"""Directions supported by topology links."""

from enum import StrEnum


class TopologyLinkDirection(StrEnum):
    """Describe how information or connectivity flows through a link."""

    UNDIRECTED = "undirected"
    SOURCE_TO_TARGET = "source_to_target"
    BIDIRECTIONAL = "bidirectional"