"""Tests for global topology graph invariants."""

from ohana_vision.topology import (
    Topology,
    TopologyDevice,
    TopologyDeviceKind,
    TopologyLayout,
    TopologyLayoutKind,
    TopologyLink,
    TopologyLinkKind,
    TopologyPosition,
)


def make_device(device_id: str) -> TopologyDevice:
    """Create a topology device for invariant tests."""
    return TopologyDevice(
        device_id=device_id,
        label=device_id.upper(),
        kind=TopologyDeviceKind.OTHER,
    )


def make_link(
    link_id: str,
    source: str,
    target: str,
    *,
    kind: TopologyLinkKind = TopologyLinkKind.ETHERNET,
) -> TopologyLink:
    """Create a topology link for invariant tests."""
    return TopologyLink(
        link_id=link_id,
        source_device_id=source,
        target_device_id=target,
        kind=kind,
    )


def test_topology_can_be_empty() -> None:
    """An empty topology must be a valid initial state."""
    topology = Topology(
        topology_id="empty",
        label="Empty topology",
    )

    assert topology.device_count == 0
    assert topology.link_count == 0
    assert topology.layout_count == 0


def test_topology_accepts_disconnected_device() -> None:
    """A device does not need a link to exist in the topology."""
    topology = Topology(
        topology_id="test",
        label="Test",
        devices=(
            make_device("connected"),
            make_device("isolated"),
        ),
    )

    assert topology.contains_device("isolated") is True
    assert topology.links_for_device("isolated") == ()


def test_topology_accepts_disconnected_components() -> None:
    """A topology may contain multiple disconnected graph components."""
    topology = Topology(
        topology_id="test",
        label="Test",
        devices=(
            make_device("first"),
            make_device("second"),
            make_device("third"),
            make_device("fourth"),
        ),
        links=(
            make_link(
                "first-second",
                "first",
                "second",
            ),
            make_link(
                "third-fourth",
                "third",
                "fourth",
            ),
        ),
    )

    assert tuple(device.device_id for device in topology.neighbor_devices("first")) == (
        "second",
    )

    assert tuple(device.device_id for device in topology.neighbor_devices("third")) == (
        "fourth",
    )


def test_topology_accepts_cycles() -> None:
    """Network cycles must remain valid topology structures."""
    topology = Topology(
        topology_id="redundant-network",
        label="Redundant network",
        devices=(
            make_device("sw-01"),
            make_device("sw-02"),
            make_device("sw-03"),
        ),
        links=(
            make_link(
                "sw-01-sw-02",
                "sw-01",
                "sw-02",
            ),
            make_link(
                "sw-02-sw-03",
                "sw-02",
                "sw-03",
            ),
            make_link(
                "sw-03-sw-01",
                "sw-03",
                "sw-01",
            ),
        ),
    )

    assert topology.link_count == 3
    assert len(topology.neighbor_devices("sw-01")) == 2


def test_topology_accepts_parallel_links() -> None:
    """Distinct relationships may connect the same devices."""
    topology = Topology(
        topology_id="test",
        label="Test",
        devices=(
            make_device("rpi-link"),
            make_device("ha-green"),
        ),
        links=(
            make_link(
                "rpi-link-ha-green-ethernet",
                "rpi-link",
                "ha-green",
            ),
            make_link(
                "rpi-link-ha-green-mqtt",
                "rpi-link",
                "ha-green",
                kind=TopologyLinkKind.MQTT,
            ),
        ),
    )

    assert topology.link_count == 2
    assert len(topology.links_for_device("rpi-link")) == 2
    assert len(topology.neighbor_devices("rpi-link")) == 1


def test_topology_accepts_partial_layout() -> None:
    """A layout does not need to position every topology device."""
    topology = Topology(
        topology_id="test",
        label="Test",
        devices=(
            make_device("internet"),
            make_device("freebox"),
            make_device("sw-01"),
        ),
        layouts=(
            TopologyLayout(
                layout_id="partial",
                label="Partial layout",
                kind=TopologyLayoutKind.CUSTOM,
                positions={
                    "internet": TopologyPosition(
                        x=100,
                        y=100,
                    ),
                },
            ),
        ),
    )

    layout = topology.layout("partial")

    assert layout is not None
    assert layout.contains_device("internet") is True
    assert layout.contains_device("freebox") is False


def test_topology_accepts_multiple_layouts() -> None:
    """The same topology may provide several visual arrangements."""
    devices = (
        make_device("internet"),
        make_device("freebox"),
    )

    topology = Topology(
        topology_id="test",
        label="Test",
        devices=devices,
        layouts=(
            TopologyLayout(
                layout_id="physical",
                label="Physical",
                kind=TopologyLayoutKind.PHYSICAL,
                positions={
                    "internet": TopologyPosition(
                        x=100,
                        y=100,
                    ),
                    "freebox": TopologyPosition(
                        x=100,
                        y=300,
                    ),
                },
            ),
            TopologyLayout(
                layout_id="logical",
                label="Logical",
                kind=TopologyLayoutKind.LOGICAL,
                positions={
                    "internet": TopologyPosition(
                        x=100,
                        y=100,
                    ),
                    "freebox": TopologyPosition(
                        x=400,
                        y=100,
                    ),
                },
            ),
        ),
    )

    assert topology.layout_count == 2
    assert topology.layout("physical") is not None
    assert topology.layout("logical") is not None


def test_topology_preserves_declaration_order() -> None:
    """Topology collections must retain architectural declaration order."""
    topology = Topology(
        topology_id="test",
        label="Test",
        devices=(
            make_device("internet"),
            make_device("freebox"),
            make_device("sw-01"),
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
        ),
    )

    assert tuple(device.device_id for device in topology.devices) == (
        "internet",
        "freebox",
        "sw-01",
    )

    assert tuple(link.link_id for link in topology.links) == (
        "internet-freebox",
        "freebox-sw-01",
    )
