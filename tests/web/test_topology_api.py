"""Tests for the infrastructure topology HTTP API."""

from typing import cast

from fastapi.testclient import TestClient

from ohanna_vision.topology import (
    Topology,
    TopologyDevice,
    TopologyDeviceKind,
    TopologyLayout,
    TopologyLayoutKind,
    TopologyLink,
    TopologyLinkKind,
    TopologyPosition,
)
from ohanna_vision.web import create_app
from ohanna_vision.web.dependencies import get_topology


def make_topology() -> Topology:
    """Create an Ohanna-House topology for API tests."""
    return Topology(
        topology_id="ohanna-house",
        label="Ohanna-House",
        devices=(
            TopologyDevice(
                device_id="internet",
                label="Internet",
                kind=TopologyDeviceKind.INTERNET,
            ),
            TopologyDevice(
                device_id="freebox",
                label="Freebox Pop",
                kind=TopologyDeviceKind.ROUTER,
                address="192.168.1.1",
            ),
        ),
        links=(
            TopologyLink(
                link_id="internet-freebox",
                source_device_id="internet",
                target_device_id="freebox",
                kind=TopologyLinkKind.ETHERNET,
                label="WAN",
            ),
        ),
        layouts=(
            TopologyLayout(
                layout_id="physical-main",
                label="Carte physique principale",
                kind=TopologyLayoutKind.PHYSICAL,
                positions={
                    "internet": TopologyPosition(
                        x=800,
                        y=80,
                        pinned=True,
                    ),
                    "freebox": TopologyPosition(
                        x=800,
                        y=220,
                        pinned=True,
                    ),
                },
            ),
        ),
    )


def make_client(
    topology: Topology | None = None,
) -> TestClient:
    """Create an application client with a topology override."""
    application = create_app()

    if topology is not None:
        application.dependency_overrides[get_topology] = lambda: cast(
            Topology,
            topology,
        )

    return TestClient(application)


def test_topology_api_is_available() -> None:
    """The topology endpoint must be exposed."""
    client = make_client(make_topology())

    response = client.get("/api/topology")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")


def test_topology_api_returns_identity() -> None:
    """The topology endpoint must expose topology identity."""
    client = make_client(make_topology())

    response = client.get("/api/topology")

    payload = response.json()

    assert payload["topology_id"] == "ohanna-house"
    assert payload["label"] == "Ohanna-House"


def test_topology_api_returns_devices() -> None:
    """The topology endpoint must expose devices."""
    client = make_client(make_topology())

    response = client.get("/api/topology")

    devices = response.json()["devices"]

    assert devices == [
        {
            "device_id": "internet",
            "label": "Internet",
            "kind": "internet",
            "node_id": None,
            "address": None,
            "metadata": {},
        },
        {
            "device_id": "freebox",
            "label": "Freebox Pop",
            "kind": "router",
            "node_id": None,
            "address": "192.168.1.1",
            "metadata": {},
        },
    ]


def test_topology_api_returns_links() -> None:
    """The topology endpoint must expose links."""
    client = make_client(make_topology())

    response = client.get("/api/topology")

    links = response.json()["links"]

    assert links == [
        {
            "link_id": "internet-freebox",
            "source_device_id": "internet",
            "target_device_id": "freebox",
            "kind": "ethernet",
            "direction": "bidirectional",
            "label": "WAN",
            "bandwidth_mbps": None,
            "metadata": {},
        },
    ]


def test_topology_api_returns_layouts() -> None:
    """The topology endpoint must expose layouts and positions."""
    client = make_client(make_topology())

    response = client.get("/api/topology")

    layouts = response.json()["layouts"]

    assert layouts == [
        {
            "layout_id": "physical-main",
            "label": "Carte physique principale",
            "kind": "physical",
            "canvas_width": 1600.0,
            "canvas_height": 900.0,
            "positions": {
                "internet": {
                    "x": 800.0,
                    "y": 80.0,
                    "layer": 0,
                    "pinned": True,
                },
                "freebox": {
                    "x": 800.0,
                    "y": 220.0,
                    "layer": 0,
                    "pinned": True,
                },
            },
            "metadata": {},
        },
    ]


def test_topology_api_returns_empty_default_topology() -> None:
    """The default application must expose a valid empty topology."""
    client = make_client()

    response = client.get("/api/topology")

    assert response.status_code == 200

    payload = response.json()

    assert payload["topology_id"] == "ohanna-house"
    assert payload["label"] == "Ohanna-House"
    assert payload["devices"] == []
    assert payload["links"] == []
    assert payload["layouts"] == []


def test_topology_api_is_documented_in_openapi() -> None:
    """The topology endpoint must be declared in OpenAPI."""
    client = make_client()

    response = client.get("/openapi.json")

    assert response.status_code == 200
    assert "/api/topology" in response.json()["paths"]
