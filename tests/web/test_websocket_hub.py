"""Tests for the Ohanna-Vision WebSocket hub."""

import asyncio
from typing import cast

from fastapi import WebSocket

from ohanna_vision.web.websocket_hub import WebSocketHub


class FakeWebSocket:
    """Minimal WebSocket double for hub tests."""

    def __init__(
        self,
        *,
        fail_on_send: bool = False,
    ) -> None:
        self.accepted = False
        self.fail_on_send = fail_on_send
        self.messages: list[dict[str, object]] = []

    async def accept(self) -> None:
        """Record connection acceptance."""
        self.accepted = True

    async def send_json(
        self,
        message: dict[str, object],
    ) -> None:
        """Record a JSON message or simulate a disconnection."""
        if self.fail_on_send:
            raise RuntimeError("WebSocket is disconnected.")

        self.messages.append(message)


def as_websocket(
    websocket: FakeWebSocket,
) -> WebSocket:
    """Cast a test double to the WebSocket interface."""
    return cast(WebSocket, websocket)


def test_websocket_hub_starts_empty() -> None:
    """A new hub must have no active connections."""
    hub = WebSocketHub()

    assert hub.connection_count == 0


def test_websocket_hub_connects_client() -> None:
    """Connecting a client must accept and register it."""
    hub = WebSocketHub()
    websocket = FakeWebSocket()

    asyncio.run(hub.connect(as_websocket(websocket)))

    assert websocket.accepted is True
    assert hub.connection_count == 1


def test_websocket_hub_disconnects_client() -> None:
    """Disconnecting a client must remove it."""
    hub = WebSocketHub()
    websocket = FakeWebSocket()
    typed_websocket = as_websocket(websocket)

    asyncio.run(hub.connect(typed_websocket))
    hub.disconnect(typed_websocket)

    assert hub.connection_count == 0


def test_websocket_hub_sends_message_to_one_client() -> None:
    """The hub must send JSON to one client."""
    hub = WebSocketHub()
    websocket = FakeWebSocket()
    typed_websocket = as_websocket(websocket)

    asyncio.run(hub.connect(typed_websocket))
    asyncio.run(
        hub.send(
            typed_websocket,
            {
                "type": "runtime.updated",
            },
        )
    )

    assert websocket.messages == [
        {
            "type": "runtime.updated",
        }
    ]


def test_websocket_hub_broadcasts_to_all_clients() -> None:
    """A broadcast must reach every active client."""
    hub = WebSocketHub()
    first = FakeWebSocket()
    second = FakeWebSocket()

    asyncio.run(hub.connect(as_websocket(first)))
    asyncio.run(hub.connect(as_websocket(second)))

    asyncio.run(
        hub.broadcast(
            {
                "type": "observation.received",
            }
        )
    )

    assert first.messages == [
        {
            "type": "observation.received",
        }
    ]
    assert second.messages == [
        {
            "type": "observation.received",
        }
    ]


def test_websocket_hub_removes_failed_connections() -> None:
    """Failed clients must be removed during a broadcast."""
    hub = WebSocketHub()
    active = FakeWebSocket()
    disconnected = FakeWebSocket(fail_on_send=True)

    asyncio.run(hub.connect(as_websocket(active)))
    asyncio.run(hub.connect(as_websocket(disconnected)))

    asyncio.run(
        hub.broadcast(
            {
                "type": "runtime.updated",
            }
        )
    )

    assert hub.connection_count == 1
    assert active.messages == [
        {
            "type": "runtime.updated",
        }
    ]