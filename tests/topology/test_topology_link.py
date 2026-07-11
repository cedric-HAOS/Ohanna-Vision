"""Tests for topology links."""

import math

import pytest

from ohanna_vision.topology import (
    TopologyLink,
    TopologyLinkDirection,
    TopologyLinkKind,
)


def test_topology_link_stores_identity() -> None:
    """A topology link must expose its architectural identity."""
    link = TopologyLink(
        link_id="sw-01-sw-02",
        source_device_id="sw-01",
        target_device_id="sw-02",
        kind=TopologyLinkKind.ETHERNET,
    )

    assert link.link_id == "sw-01-sw-02"
    assert link.source_device_id == "sw-01"
    assert link.target_device_id == "sw-02"
    assert link.kind is TopologyLinkKind.ETHERNET


def test_topology_link_is_bidirectional_by_default() -> None:
    """Topology links must default to bidirectional exchanges."""
    link = TopologyLink(
        link_id="sw-01-sw-02",
        source_device_id="sw-01",
        target_device_id="sw-02",
        kind=TopologyLinkKind.ETHERNET,
    )

    assert (
        link.direction
        is TopologyLinkDirection.BIDIRECTIONAL
    )


def test_topology_link_can_be_directional() -> None:
    """A topology link may represent a one-way logical flow."""
    link = TopologyLink(
        link_id="linky-to-mqtt",
        source_device_id="rpi-link",
        target_device_id="ha-green",
        kind=TopologyLinkKind.MQTT,
        direction=TopologyLinkDirection.SOURCE_TO_TARGET,
    )

    assert (
        link.direction
        is TopologyLinkDirection.SOURCE_TO_TARGET
    )


def test_topology_link_can_store_bandwidth() -> None:
    """A topology link may expose its nominal bandwidth."""
    link = TopologyLink(
        link_id="sw-01-sw-02",
        source_device_id="sw-01",
        target_device_id="sw-02",
        kind=TopologyLinkKind.ETHERNET,
        bandwidth_mbps=10_000,
    )

    assert link.bandwidth_mbps == 10_000


def test_topology_link_can_store_label() -> None:
    """A topology link may expose a display label."""
    link = TopologyLink(
        link_id="sw-01-sw-02",
        source_device_id="sw-01",
        target_device_id="sw-02",
        kind=TopologyLinkKind.ETHERNET,
        label="Ethernet 10 Gb",
    )

    assert link.label == "Ethernet 10 Gb"


def test_topology_link_normalizes_text_values() -> None:
    """Textual topology link values must be normalized."""
    link = TopologyLink(
        link_id="  sw-01-sw-02  ",
        source_device_id="  sw-01  ",
        target_device_id="  sw-02  ",
        kind=TopologyLinkKind.ETHERNET,
        label="  Backbone 10 Gb  ",
    )

    assert link.link_id == "sw-01-sw-02"
    assert link.source_device_id == "sw-01"
    assert link.target_device_id == "sw-02"
    assert link.label == "Backbone 10 Gb"


def test_topology_link_normalizes_empty_label() -> None:
    """A blank optional label must be normalized to None."""
    link = TopologyLink(
        link_id="sw-01-sw-02",
        source_device_id="sw-01",
        target_device_id="sw-02",
        kind=TopologyLinkKind.ETHERNET,
        label="   ",
    )

    assert link.label is None


def test_topology_link_rejects_empty_link_id() -> None:
    """A topology link must have a non-empty identifier."""
    with pytest.raises(
        ValueError,
        match="link_id must not be empty",
    ):
        TopologyLink(
            link_id="   ",
            source_device_id="sw-01",
            target_device_id="sw-02",
            kind=TopologyLinkKind.ETHERNET,
        )


def test_topology_link_rejects_empty_source_device_id() -> None:
    """A topology link must have a source device."""
    with pytest.raises(
        ValueError,
        match="source_device_id must not be empty",
    ):
        TopologyLink(
            link_id="sw-01-sw-02",
            source_device_id="   ",
            target_device_id="sw-02",
            kind=TopologyLinkKind.ETHERNET,
        )


def test_topology_link_rejects_empty_target_device_id() -> None:
    """A topology link must have a target device."""
    with pytest.raises(
        ValueError,
        match="target_device_id must not be empty",
    ):
        TopologyLink(
            link_id="sw-01-sw-02",
            source_device_id="sw-01",
            target_device_id="   ",
            kind=TopologyLinkKind.ETHERNET,
        )


def test_topology_link_rejects_self_reference() -> None:
    """A topology link cannot connect a device to itself."""
    with pytest.raises(
        ValueError,
        match="source_device_id and target_device_id must differ",
    ):
        TopologyLink(
            link_id="sw-01-self",
            source_device_id="sw-01",
            target_device_id="sw-01",
            kind=TopologyLinkKind.ETHERNET,
        )


@pytest.mark.parametrize(
    "bandwidth_mbps",
    [
        0,
        -1,
        -1000,
    ],
)
def test_topology_link_rejects_invalid_bandwidth(
    bandwidth_mbps: float,
) -> None:
    """A declared bandwidth must be strictly positive."""
    with pytest.raises(
        ValueError,
        match="bandwidth_mbps must be greater than zero",
    ):
        TopologyLink(
            link_id="sw-01-sw-02",
            source_device_id="sw-01",
            target_device_id="sw-02",
            kind=TopologyLinkKind.ETHERNET,
            bandwidth_mbps=bandwidth_mbps,
        )


def test_topology_link_copies_metadata() -> None:
    """External metadata changes must not mutate the link."""
    metadata: dict[str, object] = {
        "source_port": 1,
        "target_port": 8,
    }

    link = TopologyLink(
        link_id="sw-01-sw-02",
        source_device_id="sw-01",
        target_device_id="sw-02",
        kind=TopologyLinkKind.ETHERNET,
        metadata=metadata,
    )

    metadata["target_port"] = 4

    assert link.metadata["source_port"] == 1
    assert link.metadata["target_port"] == 8


def test_topology_link_metadata_is_immutable() -> None:
    """Topology link metadata must not be mutable."""
    link = TopologyLink(
        link_id="sw-01-sw-02",
        source_device_id="sw-01",
        target_device_id="sw-02",
        kind=TopologyLinkKind.ETHERNET,
        metadata={
            "source_port": 1,
            "target_port": 8,
        },
    )

    with pytest.raises(TypeError):
        link.metadata["target_port"] = 4  # type: ignore[index]


def test_topology_link_is_immutable() -> None:
    """A topology link must remain immutable after creation."""
    link = TopologyLink(
        link_id="sw-01-sw-02",
        source_device_id="sw-01",
        target_device_id="sw-02",
        kind=TopologyLinkKind.ETHERNET,
    )

    with pytest.raises(AttributeError):
        link.label = "Other link"  # type: ignore[misc]

def test_topology_link_metadata_is_deeply_immutable() -> None:
    """Nested topology link metadata must remain immutable."""
    metadata = {
        "ports": {
            "source": "10G-1",
            "target": "10G-2",
        },
    }

    link = TopologyLink(
        link_id="sw-01-sw-02",
        source_device_id="sw-01",
        target_device_id="sw-02",
        kind=TopologyLinkKind.ETHERNET,
        metadata=metadata,
    )

    metadata["ports"]["target"] = "10G-4"

    ports = link.metadata["ports"]

    assert ports["target"] == "10G-2"  # type: ignore[index]

    with pytest.raises(TypeError):
        ports["target"] = "10G-8"  # type: ignore[index]

@pytest.mark.parametrize(
    "bandwidth_mbps",
    [
        math.nan,
        math.inf,
        -math.inf,
    ],
)
def test_topology_link_rejects_non_finite_bandwidth(
    bandwidth_mbps: float,
) -> None:
    """A topology bandwidth must contain a finite numeric value."""
    with pytest.raises(
        ValueError,
        match="bandwidth_mbps must be finite",
    ):
        TopologyLink(
            link_id="sw-01-sw-02",
            source_device_id="sw-01",
            target_device_id="sw-02",
            kind=TopologyLinkKind.ETHERNET,
            bandwidth_mbps=bandwidth_mbps,
        )