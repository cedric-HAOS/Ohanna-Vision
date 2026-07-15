"""Mapping between REST observation requests and domain observations."""

from __future__ import annotations

from ohanna_vision.domain.observation import Observation
from ohanna_vision.web.observation_request import ObservationRequest


class ObservationMapper:
    """Convert REST observation requests into domain observations."""

    @staticmethod
    def to_domain(request: ObservationRequest) -> Observation:
        """Convert an observation request into a domain observation."""
        return Observation(
            capability_id=request.capability_id,
            service_id=request.service_id,
            node_id=request.node_id,
            status=request.status,
            observed_at=request.observed_at,
            latency_ms=request.latency_ms,
            metadata=dict(request.metadata),
        )
