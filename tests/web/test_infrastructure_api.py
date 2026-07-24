"""Tests for the infrastructure ingestion HTTP API."""

from fastapi.testclient import TestClient

from ohana_vision.web import create_app


def make_payload(
    *,
    infrastructure_id: str = "ohana-house",
) -> dict[str, object]:
    """Build a valid infrastructure payload."""
    return {
        "schema_version": 1,
        "infrastructure_id": infrastructure_id,
        "name": "Ohana House",
        "environment": "production",
        "metadata": {
            "version": "1.0",
            "tags": [
                "production",
                "home",
            ],
        },
        "nodes": [
            {
                "node_id": "infra-01",
                "name": "INFRA-01",
                "description": "Infrastructure server",
                "endpoint": {
                    "type": "ip",
                    "address": "192.168.1.10",
                },
            }
        ],
        "services": [
            {
                "service_id": "dns-primary",
                "name": "Primary DNS",
                "type": "dns",
                "node_id": "infra-01",
                "port": 53,
            }
        ],
    }


def test_infrastructure_api_accepts_snapshot() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.put(
        "/api/infrastructure",
        json=make_payload(),
    )

    assert response.status_code == 200
    assert response.json() == {
        "accepted": True,
        "infrastructure_id": "ohana-house",
        "node_count": 1,
        "service_count": 1,
    }


def test_infrastructure_api_stores_snapshot() -> None:
    app = create_app()
    client = TestClient(app)

    client.put(
        "/api/infrastructure",
        json=make_payload(),
    )

    snapshot = app.state.infrastructure_snapshot

    assert snapshot is not None
    assert snapshot.infrastructure_id == "ohana-house"
    assert snapshot.nodes[0].node_id == "infra-01"


def test_infrastructure_api_replaces_previous_snapshot() -> None:
    app = create_app()
    client = TestClient(app)

    first_response = client.put(
        "/api/infrastructure",
        json=make_payload(infrastructure_id="first"),
    )

    second_response = client.put(
        "/api/infrastructure",
        json=make_payload(infrastructure_id="second"),
    )

    assert first_response.status_code == 200
    assert second_response.status_code == 200

    assert app.state.infrastructure_snapshot.infrastructure_id == "second"


def test_infrastructure_api_rejects_invalid_snapshot() -> None:
    payload = make_payload()
    payload["schema_version"] = 2

    response = TestClient(create_app()).put(
        "/api/infrastructure",
        json=payload,
    )

    assert response.status_code == 422


def test_infrastructure_api_is_documented_in_openapi() -> None:
    response = TestClient(create_app()).get("/openapi.json")

    assert response.status_code == 200

    paths = response.json()["paths"]

    assert "/api/infrastructure" in paths
    assert "put" in paths["/api/infrastructure"]


def test_infrastructure_api_rejects_post() -> None:
    response = TestClient(create_app()).post(
        "/api/infrastructure",
        json=make_payload(),
    )

    assert response.status_code == 405


def test_infrastructure_api_projects_snapshot_to_topology() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.put(
        "/api/infrastructure",
        json=make_payload(),
    )

    assert response.status_code == 200

    topology_response = client.get("/api/topology")

    assert topology_response.status_code == 200

    topology = topology_response.json()

    assert topology["topology_id"] == "ohana-house"
    assert len(topology["devices"]) == 1
    assert len(topology["layouts"]) == 1

    device = topology["devices"][0]

    assert device["device_id"] == "infra-01"
    assert device["node_id"] == "infra-01"
    assert device["address"] == "192.168.1.10"


def test_infrastructure_api_replaces_previous_projection() -> None:
    app = create_app()
    client = TestClient(app)

    first_payload = make_payload()
    first_payload["nodes"][0]["node_id"] = "first"
    first_payload["services"] = []

    second_payload = make_payload()
    second_payload["nodes"][0]["node_id"] = "second"
    second_payload["services"] = []

    assert (
        client.put(
            "/api/infrastructure",
            json=first_payload,
        ).status_code
        == 200
    )

    assert (
        client.put(
            "/api/infrastructure",
            json=second_payload,
        ).status_code
        == 200
    )

    topology = app.state.topology

    assert not topology.contains_device("first")
    assert topology.contains_device("second")


def make_complete_topology_payload() -> dict[str, object]:
    """Build an infrastructure payload with a complete topology."""
    payload = make_payload()
    payload["topology"] = {
        "devices": [
            {
                "device_id": "internet",
                "label": "Internet",
                "kind": "internet",
                "node_id": None,
                "address": None,
                "metadata": {},
            },
            {
                "device_id": "infra-device",
                "label": "INFRA-01",
                "kind": "raspberry_pi",
                "node_id": "infra-01",
                "address": None,
                "metadata": {},
            },
        ],
        "links": [
            {
                "link_id": "internet-infra",
                "source_device_id": "internet",
                "target_device_id": "infra-device",
                "kind": "ethernet",
                "direction": "bidirectional",
                "label": "WAN",
                "bandwidth_mbps": 1000,
                "metadata": {},
            }
        ],
        "layouts": [
            {
                "layout_id": "physical",
                "label": "Physical",
                "kind": "physical",
                "positions": {
                    "internet": {
                        "column": 0,
                        "row": 1,
                    },
                    "infra-device": {
                        "column": 1,
                        "row": 1,
                    },
                },
                "metadata": {},
            }
        ],
        "metadata": {},
    }
    return payload


def test_infrastructure_api_projects_complete_topology() -> None:
    app = create_app()
    client = TestClient(app)

    response = client.put(
        "/api/infrastructure",
        json=make_complete_topology_payload(),
    )

    assert response.status_code == 200

    topology = client.get("/api/topology").json()

    assert [device["device_id"] for device in topology["devices"]] == [
        "internet",
        "infra-device",
    ]
    assert topology["links"][0]["link_id"] == "internet-infra"
    assert topology["layouts"][0]["positions"]["internet"] == {
        "x": 150.0,
        "y": 410.0,
        "layer": 0,
        "pinned": True,
    }
    assert topology["layouts"][0]["canvas_width"] == 600.0
    assert topology["layouts"][0]["canvas_height"] == 560.0
