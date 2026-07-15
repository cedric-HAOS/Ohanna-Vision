"""Tests for topology devices."""

import pytest

from ohanna_vision.topology import (
    TopologyDevice,
    TopologyDeviceKind,
)


def test_topology_device_stores_identity() -> None:
    """A topology device must expose its architectural identity."""
    device = TopologyDevice(
        device_id="sw-01",
        label="SW-01",
        kind=TopologyDeviceKind.SWITCH,
    )

    assert device.device_id == "sw-01"
    assert device.label == "SW-01"
    assert device.kind is TopologyDeviceKind.SWITCH


def test_topology_device_can_reference_runtime_node() -> None:
    """A topology device may reference a supervised runtime node."""
    device = TopologyDevice(
        device_id="ha-green",
        label="HA-Green",
        kind=TopologyDeviceKind.HOME_ASSISTANT,
        node_id="ha-green",
        address="192.168.1.12",
    )

    assert device.node_id == "ha-green"
    assert device.address == "192.168.1.12"


def test_topology_device_can_exist_without_runtime_node() -> None:
    """A purely architectural device does not require a runtime node."""
    device = TopologyDevice(
        device_id="internet",
        label="Internet",
        kind=TopologyDeviceKind.INTERNET,
    )

    assert device.node_id is None
    assert device.address is None


def test_topology_device_normalizes_text_values() -> None:
    """Textual topology values must be normalized."""
    device = TopologyDevice(
        device_id="  sw-01  ",
        label="  Main switch  ",
        kind=TopologyDeviceKind.SWITCH,
        node_id="  infra-01  ",
        address="  192.168.1.2  ",
    )

    assert device.device_id == "sw-01"
    assert device.label == "Main switch"
    assert device.node_id == "infra-01"
    assert device.address == "192.168.1.2"


def test_topology_device_normalizes_empty_optional_values() -> None:
    """Blank optional values must be converted to None."""
    device = TopologyDevice(
        device_id="sw-01",
        label="SW-01",
        kind=TopologyDeviceKind.SWITCH,
        node_id="   ",
        address="   ",
    )

    assert device.node_id is None
    assert device.address is None


def test_topology_device_rejects_empty_device_id() -> None:
    """A topology device must have a non-empty identifier."""
    with pytest.raises(
        ValueError,
        match="device_id must not be empty",
    ):
        TopologyDevice(
            device_id="   ",
            label="SW-01",
            kind=TopologyDeviceKind.SWITCH,
        )


def test_topology_device_rejects_empty_label() -> None:
    """A topology device must have a non-empty display label."""
    with pytest.raises(
        ValueError,
        match="label must not be empty",
    ):
        TopologyDevice(
            device_id="sw-01",
            label="   ",
            kind=TopologyDeviceKind.SWITCH,
        )


def test_topology_device_copies_metadata() -> None:
    """External metadata changes must not mutate the device."""
    metadata: dict[str, object] = {
        "manufacturer": "TRENDnet",
        "ports": 8,
    }

    device = TopologyDevice(
        device_id="sw-01",
        label="SW-01",
        kind=TopologyDeviceKind.SWITCH,
        metadata=metadata,
    )

    metadata["ports"] = 16

    assert device.metadata["manufacturer"] == "TRENDnet"
    assert device.metadata["ports"] == 8


def test_topology_device_metadata_is_immutable() -> None:
    """Topology metadata must not be mutable through the device."""
    device = TopologyDevice(
        device_id="sw-01",
        label="SW-01",
        kind=TopologyDeviceKind.SWITCH,
        metadata={"ports": 8},
    )

    with pytest.raises(TypeError):
        device.metadata["ports"] = 16  # type: ignore[index]


def test_topology_device_is_immutable() -> None:
    """A topology device must remain immutable after creation."""
    device = TopologyDevice(
        device_id="sw-01",
        label="SW-01",
        kind=TopologyDeviceKind.SWITCH,
    )

    with pytest.raises(AttributeError):
        device.label = "Other switch"  # type: ignore[misc]


def test_topology_device_metadata_is_deeply_immutable() -> None:
    """Nested topology device metadata must remain immutable."""
    metadata = {
        "network": {
            "interfaces": [
                "eth0",
                "eth1",
            ],
        },
    }

    device = TopologyDevice(
        device_id="sw-01",
        label="SW-01",
        kind=TopologyDeviceKind.SWITCH,
        metadata=metadata,
    )

    metadata["network"]["interfaces"].append("eth2")

    network = device.metadata["network"]

    assert network["interfaces"] == (  # type: ignore[index]
        "eth0",
        "eth1",
    )

    with pytest.raises(TypeError):
        network["interfaces"] = ()  # type: ignore[index]
