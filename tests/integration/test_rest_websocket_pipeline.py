"""Integration test for REST observation ingestion and WebSocket broadcast."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from fastapi.testclient import TestClient

from ohanna_vision.domain.observation import Observation
from ohanna_vision.runtime import ObservationProcessor
from ohanna_vision.web.app import create_app
from ohanna_vision.web.dependencies import get_observation_processor


@dataclass(frozen=True)
class FakeProcessingResult:
    """Minimal successful processing result."""

    accepted: bool = True


class FakeObservationProcessor:
    """Observation processor accepting and recording observations."""

    def __init__(self) -> None:
        self.observations: list[Observation] = []

    def process(
        self,
        observation: Observation,
    ) -> FakeProcessingResult:
        """Record and accept an observation."""
        self.observations.append(observation)

        return FakeProcessingResult()


def test_post_observation_is_received_by_websocket_client() -> None:
    """An accepted REST observation must reach connected WebSocket clients."""
    processor = FakeObservationProcessor()
    application = create_app()

    application.dependency_overrides[get_observation_processor] = lambda: cast(
        ObservationProcessor,
        processor,
    )

    client = TestClient(application)

    with client.websocket_connect("/ws") as websocket:
        connected_message = websocket.receive_json()

        response = client.post(
            "/api/observations",
            json={
                "capability_id": "dns.resolve",
                "service_id": "dns-primary",
                "node_id": "infra-01",
                "status": "healthy",
                "observed_at": "2026-07-11T16:30:00+00:00",
                "latency_ms": 12.5,
                "metadata": {
                    "hostname": "example.com",
                },
            },
        )

        message = websocket.receive_json()

    assert response.status_code == 202
    assert response.json() == {
        "accepted": True,
        "message": "Observation accepted.",
    }

    assert len(processor.observations) == 1

    assert connected_message == {
        "type": "connected",
        "message": "Ohanna Vision WebSocket connected",
    }

    assert message == {
        "type": "observation.accepted",
        "observation_id": str(processor.observations[0].observation_id),
        "capability_id": "dns.resolve",
        "service_id": "dns-primary",
        "node_id": "infra-01",
        "status": "healthy",
    }
