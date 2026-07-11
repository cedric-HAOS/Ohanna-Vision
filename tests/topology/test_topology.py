"""Tests for complete infrastructure topologies."""

import pytest

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


def make_device(
    device_id: str,
    *,
    kind: TopologyDeviceKind = TopologyDeviceKind.OTHER,
) -> TopologyDevice:
    """Create a topology device for tests."""
    return TopologyDevice(
        device_id=device_id,
        label=device_id.upper(),
        kind=kind,
    )


def make_link(
    link_id: str,
    source_device_id: str,
    target_device_id: str,
) -> TopologyLink:
    """Create an Ethernet topology link for tests."""
    return TopologyLink(
        link_id=link_id,
        source_device_id=source_device_id,
        target_device_id=target_device_id,
        kind=TopologyLinkKind.ETHERNET,
    )


def make_topology() -> Topology:
    """Create a representative Ohanna-House topology."""
    internet = make_device(
        "internet",
        kind=TopologyDeviceKind.INTERNET,
    )
    freebox = make_device(
        "freebox",
        kind=TopologyDeviceKind.ROUTER,
    )
    sw_01 = make_device(
        "sw-01",
        kind=TopologyDeviceKind.SWITCH,
    )
    ha_green = make_device(
        "ha-green",
        kind=TopologyDeviceKind.HOME_ASSISTANT,
    )

    return Topology(
        topology_id="ohanna-house",
        label="Ohanna-House",
        devices=(
            internet,
            freebox,
            sw_01,
            ha_green,
        ),
        links=(
            make_link(
                "internet-freebox",
                "internet",
                "freebox",
            ),
            make_link(
                "freebox-sw-01",
                "freebox",
                "sw-01",
            ),
            make_link(
                "sw-01-ha-green",
                "sw-01",
                "ha-green",
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
                    ),
                    "freebox": TopologyPosition(
                        x=800,
                        y=220,
                    ),
                    "sw-01": TopologyPosition(
                        x=800,
                        y=380,
                    ),
                    "ha-green": TopologyPosition(
                        x=800,
                        y=560,
                    ),
                },
            ),
        ),
    )


def test_topology_stores_identity() -> None:
    """A topology must expose its architectural identity."""
    topology = Topology(
        topology_id="ohanna-house",
        label="Ohanna-House",
    )

    assert topology.topology_id == "ohanna-house"
    assert topology.label == "Ohanna-House"


def test_topology_normalizes_identity() -> None:
    """Topology identity values must be normalized."""
    topology = Topology(
        topology_id="  ohanna-house  ",
        label="  Ohanna-House  ",
    )

    assert topology.topology_id == "ohanna-house"
    assert topology.label == "Ohanna-House"


def test_topology_stores_devices_links_and_layouts() -> None:
    """A topology must store its complete graph definition."""
    topology = make_topology()

    assert topology.device_count == 4
    assert topology.link_count == 3
    assert topology.layout_count == 1


def test_topology_returns_device_by_identifier() -> None:
    """A topology must return devices by identifier."""
    topology = make_topology()

    device = topology.device("sw-01")

    assert device is not None
    assert device.device_id == "sw-01"


def test_topology_normalizes_lookup_identifiers() -> None:
    """Topology lookups must normalize identifiers."""
    topology = make_topology()

    assert topology.device("  sw-01  ") is not None
    assert topology.link("  freebox-sw-01  ") is not None
    assert topology.layout("  physical-main  ") is not None


def test_topology_returns_none_for_unknown_identifiers() -> None:
    """Unknown topology identifiers must return None."""
    topology = make_topology()

    assert topology.device("unknown") is None
    assert topology.link("unknown") is None
    assert topology.layout("unknown") is None


def test_topology_returns_none_for_empty_identifiers() -> None:
    """Blank topology lookups must return None."""
    topology = make_topology()

    assert topology.device("   ") is None
    assert topology.link("   ") is None
    assert topology.layout("   ") is None


def test_topology_reports_contained_elements() -> None:
    """A topology must report its contained graph elements."""
    topology = make_topology()

    assert topology.contains_device("sw-01") is True
    assert topology.contains_link("freebox-sw-01") is True
    assert topology.contains_layout("physical-main") is True

    assert topology.contains_device("unknown") is False
    assert topology.contains_link("unknown") is False
    assert topology.contains_layout("unknown") is False


def test_topology_returns_links_for_device() -> None:
    """A topology must return every link connected to a device."""
    topology = make_topology()

    links = topology.links_for_device("sw-01")

    assert tuple(link.link_id for link in links) == (
        "freebox-sw-01",
        "sw-01-ha-green",
    )


def test_topology_returns_no_links_for_unknown_device() -> None:
    """An unknown device must not expose topology links."""
    topology = make_topology()

    assert topology.links_for_device("unknown") == ()
    assert topology.links_for_device("   ") == ()


def test_topology_returns_outgoing_links() -> None:
    """A topology must return outgoing links for a device."""
    topology = make_topology()

    links = topology.outgoing_links("sw-01")

    assert tuple(link.link_id for link in links) == (
        "sw-01-ha-green",
    )


def test_topology_returns_incoming_links() -> None:
    """A topology must return incoming links for a device."""
    topology = make_topology()

    links = topology.incoming_links("sw-01")

    assert tuple(link.link_id for link in links) == (
        "freebox-sw-01",
    )


def test_topology_returns_neighbor_devices() -> None:
    """A topology must return directly connected devices."""
    topology = make_topology()

    neighbors = topology.neighbor_devices("sw-01")

    assert tuple(device.device_id for device in neighbors) == (
        "freebox",
        "ha-green",
    )


def test_topology_returns_each_neighbor_only_once() -> None:
    """Duplicate relationships must not duplicate neighboring devices."""
    first = make_device("first")
    second = make_device("second")

    topology = Topology(
        topology_id="test",
        label="Test",
        devices=(
            first,
            second,
        ),
        links=(
            make_link(
                "first-second-physical",
                "first",
                "second",
            ),
            TopologyLink(
                link_id="first-second-logical",
                source_device_id="first",
                target_device_id="second",
                kind=TopologyLinkKind.LOGICAL,
            ),
        ),
    )

    neighbors = topology.neighbor_devices("first")

    assert tuple(device.device_id for device in neighbors) == (
        "second",
    )


def test_topology_rejects_empty_topology_id() -> None:
    """A topology must have a non-empty identifier."""
    with pytest.raises(
        ValueError,
        match="topology_id must not be empty",
    ):
        Topology(
            topology_id="   ",
            label="Ohanna-House",
        )


def test_topology_rejects_empty_label() -> None:
    """A topology must have a non-empty label."""
    with pytest.raises(
        ValueError,
        match="label must not be empty",
    ):
        Topology(
            topology_id="ohanna-house",
            label="   ",
        )


def test_topology_rejects_duplicate_device_identifiers() -> None:
    """Device identifiers must remain unique in a topology."""
    with pytest.raises(
        ValueError,
        match="device identifiers must be unique",
    ):
        Topology(
            topology_id="test",
            label="Test",
            devices=(
                make_device("sw-01"),
                make_device("sw-01"),
            ),
        )


def test_topology_rejects_duplicate_link_identifiers() -> None:
    """Link identifiers must remain unique in a topology."""
    first = make_device("first")
    second = make_device("second")

    with pytest.raises(
        ValueError,
        match="link identifiers must be unique",
    ):
        Topology(
            topology_id="test",
            label="Test",
            devices=(
                first,
                second,
            ),
            links=(
                make_link(
                    "first-second",
                    "first",
                    "second",
                ),
                make_link(
                    "first-second",
                    "first",
                    "second",
                ),
            ),
        )


def test_topology_rejects_duplicate_layout_identifiers() -> None:
    """Layout identifiers must remain unique in a topology."""
    layout = TopologyLayout(
        layout_id="physical-main",
        label="Physical",
        kind=TopologyLayoutKind.PHYSICAL,
    )

    with pytest.raises(
        ValueError,
        match="layout identifiers must be unique",
    ):
        Topology(
            topology_id="test",
            label="Test",
            layouts=(
                layout,
                layout,
            ),
        )


def test_topology_rejects_unknown_link_source() -> None:
    """Every topology link source must reference a known device."""
    target = make_device("target")

    with pytest.raises(
        ValueError,
        match="link source device does not exist: source",
    ):
        Topology(
            topology_id="test",
            label="Test",
            devices=(target,),
            links=(
                make_link(
                    "source-target",
                    "source",
                    "target",
                ),
            ),
        )


def test_topology_rejects_unknown_link_target() -> None:
    """Every topology link target must reference a known device."""
    source = make_device("source")

    with pytest.raises(
        ValueError,
        match="link target device does not exist: target",
    ):
        Topology(
            topology_id="test",
            label="Test",
            devices=(source,),
            links=(
                make_link(
                    "source-target",
                    "source",
                    "target",
                ),
            ),
        )


def test_topology_rejects_unknown_layout_device() -> None:
    """Every layout position must reference a known device."""
    layout = TopologyLayout(
        layout_id="physical-main",
        label="Physical",
        kind=TopologyLayoutKind.PHYSICAL,
        positions={
            "unknown": TopologyPosition(
                x=100,
                y=200,
            ),
        },
    )

    with pytest.raises(
        ValueError,
        match="layout position device does not exist: unknown",
    ):
        Topology(
            topology_id="test",
            label="Test",
            layouts=(layout,),
        )


def test_topology_copies_device_collection() -> None:
    """External device collection changes must not mutate a topology."""
    devices = [
        make_device("first"),
    ]

    topology = Topology(
        topology_id="test",
        label="Test",
        devices=tuple(devices),
    )

    devices.append(make_device("second"))

    assert topology.device_count == 1
    assert topology.contains_device("second") is False


def test_topology_collections_are_tuples() -> None:
    """Topology collections must be exposed as immutable tuples."""
    topology = make_topology()

    assert isinstance(topology.devices, tuple)
    assert isinstance(topology.links, tuple)
    assert isinstance(topology.layouts, tuple)


def test_topology_copies_metadata() -> None:
    """External metadata changes must not mutate a topology."""
    metadata: dict[str, object] = {
        "description": "Ohanna-House topology",
    }

    topology = Topology(
        topology_id="ohanna-house",
        label="Ohanna-House",
        metadata=metadata,
    )

    metadata["description"] = "Changed"

    assert (
        topology.metadata["description"]
        == "Ohanna-House topology"
    )


def test_topology_metadata_is_immutable() -> None:
    """Topology metadata must not be mutable."""
    topology = Topology(
        topology_id="ohanna-house",
        label="Ohanna-House",
        metadata={
            "description": "Ohanna-House topology",
        },
    )

    with pytest.raises(TypeError):
        topology.metadata["description"] = "Changed"  # type: ignore[index]


def test_topology_is_immutable() -> None:
    """A topology must remain immutable after creation."""
    topology = make_topology()

    with pytest.raises(AttributeError):
        topology.label = "Other"  # type: ignore[misc]

def test_topology_metadata_is_deeply_immutable() -> None:
    """Nested topology metadata must remain immutable."""
    metadata = {
        "owners": [
            "Ohanna-House",
        ],
        "configuration": {
            "version": 1,
        },
    }

    topology = Topology(
        topology_id="ohanna-house",
        label="Ohanna-House",
        metadata=metadata,
    )

    metadata["owners"].append("Other")
    metadata["configuration"]["version"] = 2

    assert topology.metadata["owners"] == (
        "Ohanna-House",
    )

    configuration = topology.metadata["configuration"]

    assert configuration["version"] == 1  # type: ignore[index]