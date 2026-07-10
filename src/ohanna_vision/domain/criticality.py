"""Criticality levels used by the health engine."""

from enum import StrEnum


class Criticality(StrEnum):
    """Represent the importance of an infrastructure capability."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    CRITICAL = "critical"