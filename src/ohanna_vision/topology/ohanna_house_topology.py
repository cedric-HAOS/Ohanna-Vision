"""Ohanna-House infrastructure topology definition."""

from ohanna_vision.topology.topology import Topology
from ohanna_vision.topology.topology_device import TopologyDevice
from ohanna_vision.topology.topology_device_kind import (
    TopologyDeviceKind,
)
from ohanna_vision.topology.topology_layout import TopologyLayout
from ohanna_vision.topology.topology_layout_kind import (
    TopologyLayoutKind,
)
from ohanna_vision.topology.topology_link import TopologyLink
from ohanna_vision.topology.topology_link_direction import (
    TopologyLinkDirection,
)
from ohanna_vision.topology.topology_link_kind import (
    TopologyLinkKind,
)
from ohanna_vision.topology.topology_position import (
    TopologyPosition,
)

_LAYOUT_MARGIN_X = 150
_LAYOUT_MARGIN_Y = 150
_LAYOUT_COLUMN_SPACING = 300
_LAYOUT_ROW_SPACING = 260
_LAYOUT_COLUMN_COUNT = 6
_LAYOUT_ROW_COUNT = 3


def _grid_position(
    *,
    column: int,
    row: int,
    pinned: bool = True,
) -> TopologyPosition:
    """Convert a logical grid position into canvas coordinates."""
    return TopologyPosition(
        x=_LAYOUT_MARGIN_X + column * _LAYOUT_COLUMN_SPACING,
        y=_LAYOUT_MARGIN_Y + row * _LAYOUT_ROW_SPACING,
        layer=column,
        pinned=pinned,
    )


def build_ohanna_house_topology() -> Topology:
    """Build the physical topology of Ohanna-House."""
    return Topology(
        topology_id="ohanna-house",
        label="Ohanna-House",
        devices=_build_devices(),
        links=_build_links(),
        layouts=(_build_physical_layout(),),
        metadata={
            "description": ("Physical infrastructure topology of Ohanna-House."),
            "version": 1,
        },
    )


def _build_devices() -> tuple[TopologyDevice, ...]:
    """Build devices displayed on the infrastructure map."""
    return (
        TopologyDevice(
            device_id="internet",
            label="Internet",
            kind=TopologyDeviceKind.INTERNET,
            metadata={
                "role": "external_network",
            },
        ),
        TopologyDevice(
            device_id="freebox",
            label="Freebox Pop",
            kind=TopologyDeviceKind.ROUTER,
            metadata={
                "role": "internet_gateway",
            },
        ),
        TopologyDevice(
            device_id="sw-01",
            label="SW-01",
            kind=TopologyDeviceKind.SWITCH,
            metadata={
                "role": "core_switch",
                "manufacturer": "TRENDnet",
                "model": "TEG-S762",
            },
        ),
        TopologyDevice(
            device_id="sw-02",
            label="SW-02",
            kind=TopologyDeviceKind.SWITCH,
            metadata={
                "role": "distribution_switch",
                "manufacturer": "TRENDnet",
                "model": "TEG-S762",
            },
        ),
        TopologyDevice(
            device_id="sw-03",
            label="SW-03",
            kind=TopologyDeviceKind.SWITCH,
            metadata={
                "role": "access_switch",
                "manufacturer": "Linksys",
            },
        ),
        TopologyDevice(
            device_id="ap-01",
            label="AP-01",
            kind=TopologyDeviceKind.ACCESS_POINT,
            metadata={
                "role": "wireless_access_point",
                "manufacturer": "Linksys",
                "model": "LAPAC1750",
            },
        ),
        TopologyDevice(
            device_id="rpi-link",
            label="RPI-LINK",
            kind=TopologyDeviceKind.RASPBERRY_PI,
            node_id="rpi-link",
            metadata={
                "role": "linky_gateway",
                "connection": "wifi",
            },
        ),
        TopologyDevice(
            device_id="ha-green",
            label="HA-Green",
            kind=TopologyDeviceKind.HOME_ASSISTANT,
            node_id="ha-green",
            metadata={
                "role": "home_automation_controller",
            },
        ),
        TopologyDevice(
            device_id="rpi-zwave",
            label="RPI-ZWAVE",
            kind=TopologyDeviceKind.RASPBERRY_PI,
            node_id="rpi-zwave",
            metadata={
                "role": "zwave_gateway",
            },
        ),
    )


def _build_links() -> tuple[TopologyLink, ...]:
    """Build physical links between Ohanna-House devices."""
    bidirectional = TopologyLinkDirection.BIDIRECTIONAL

    return (
        TopologyLink(
            link_id="internet-freebox",
            source_device_id="internet",
            target_device_id="freebox",
            kind=TopologyLinkKind.ETHERNET,
            direction=bidirectional,
            label="WAN",
            metadata={
                "role": "internet_uplink",
            },
        ),
        TopologyLink(
            link_id="freebox-sw-01",
            source_device_id="freebox",
            target_device_id="sw-01",
            kind=TopologyLinkKind.ETHERNET,
            direction=bidirectional,
            label="Ethernet 2.5 Gb",
            bandwidth_mbps=2500,
            metadata={
                "role": "gateway_uplink",
            },
        ),
        TopologyLink(
            link_id="sw-01-sw-02",
            source_device_id="sw-01",
            target_device_id="sw-02",
            kind=TopologyLinkKind.ETHERNET,
            direction=bidirectional,
            label="Ethernet 10 Gb",
            bandwidth_mbps=10_000,
            metadata={
                "role": "network_backbone",
            },
        ),
        TopologyLink(
            link_id="sw-02-sw-03",
            source_device_id="sw-02",
            target_device_id="sw-03",
            kind=TopologyLinkKind.ETHERNET,
            direction=bidirectional,
            label="Ethernet 1 Gb",
            bandwidth_mbps=1000,
            metadata={
                "role": "access_uplink",
            },
        ),
        TopologyLink(
            link_id="sw-01-ap-01",
            source_device_id="sw-01",
            target_device_id="ap-01",
            kind=TopologyLinkKind.ETHERNET,
            direction=bidirectional,
            label="Ethernet 1 Gb",
            bandwidth_mbps=1000,
            metadata={
                "role": "wireless_uplink",
            },
        ),
        TopologyLink(
            link_id="ap-01-rpi-link",
            source_device_id="ap-01",
            target_device_id="rpi-link",
            kind=TopologyLinkKind.WIFI,
            direction=bidirectional,
            label="Wi-Fi",
            metadata={
                "role": "wireless_access",
            },
        ),
        TopologyLink(
            link_id="sw-03-ha-green",
            source_device_id="sw-03",
            target_device_id="ha-green",
            kind=TopologyLinkKind.ETHERNET,
            direction=bidirectional,
            label="Ethernet 1 Gb",
            bandwidth_mbps=1000,
        ),
        TopologyLink(
            link_id="sw-03-rpi-zwave",
            source_device_id="sw-03",
            target_device_id="rpi-zwave",
            kind=TopologyLinkKind.ETHERNET,
            direction=bidirectional,
            label="Ethernet 1 Gb",
            bandwidth_mbps=1000,
        ),
    )


def _build_physical_layout() -> TopologyLayout:
    """Build the primary physical infrastructure layout."""
    return TopologyLayout(
        layout_id="ohanna-house-physical",
        label="Carte physique Ohanna-House",
        kind=TopologyLayoutKind.PHYSICAL,
        canvas_width=(
            2 * _LAYOUT_MARGIN_X
            + (_LAYOUT_COLUMN_COUNT - 1) * _LAYOUT_COLUMN_SPACING
        ),
        canvas_height=(
            2 * _LAYOUT_MARGIN_Y
            + (_LAYOUT_ROW_COUNT - 1) * _LAYOUT_ROW_SPACING
        ),
        positions={
            "internet": _grid_position(column=0, row=1),
            "freebox": _grid_position(column=1, row=1),
            "sw-01": _grid_position(column=2, row=1),
            "ap-01": _grid_position(column=3, row=0),
            "sw-02": _grid_position(column=3, row=1),
            "rpi-link": _grid_position(column=4, row=0),
            "sw-03": _grid_position(column=4, row=1),
            "ha-green": _grid_position(column=5, row=1),
            "rpi-zwave": _grid_position(column=5, row=2),
        },
        metadata={
            "description": ("Primary physical infrastructure map."),
        },
    )
