"""Health evaluation policies."""

from dataclasses import dataclass
from datetime import timedelta

from ohana_vision.domain.criticality import Criticality


@dataclass(frozen=True, slots=True)
class CapabilityHealthPolicy:
    """Define health rules for one infrastructure capability."""

    node_id: str
    service_id: str
    capability_id: str
    criticality: Criticality = Criticality.NORMAL
    stale_after: timedelta | None = None

    def __post_init__(self) -> None:
        """Validate policy invariants."""

        if not self.node_id.strip():
            raise ValueError("node_id must not be empty.")

        if not self.service_id.strip():
            raise ValueError("service_id must not be empty.")

        if not self.capability_id.strip():
            raise ValueError("capability_id must not be empty.")

        if self.stale_after is not None and self.stale_after <= timedelta():
            raise ValueError("stale_after must be greater than zero.")

    @property
    def key(self) -> tuple[str, str, str]:
        """Return the capability key targeted by the policy."""

        return (
            self.node_id,
            self.service_id,
            self.capability_id,
        )
