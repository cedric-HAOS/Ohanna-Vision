"""Kinds of links represented in the infrastructure topology."""

from enum import StrEnum


class TopologyLinkKind(StrEnum):
    """Identify the physical or logical nature of a topology link."""

    ETHERNET = "ethernet"
    WIFI = "wifi"
    WIREGUARD = "wireguard"
    ZIGBEE = "zigbee"
    ZWAVE = "zwave"
    MQTT = "mqtt"
    USB = "usb"
    SERIAL = "serial"
    LOGICAL = "logical"
    OTHER = "other"