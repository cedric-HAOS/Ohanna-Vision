"""WebSocket connection management for Ohana-Vision."""

from collections.abc import Mapping

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class WebSocketHub:
    """Manage active WebSocket clients and JSON broadcasts."""

    def __init__(self) -> None:
        """Initialize an empty WebSocket connection registry."""
        self._connections: set[WebSocket] = set()

    @property
    def connection_count(self) -> int:
        """Return the number of active WebSocket connections."""
        return len(self._connections)

    async def connect(self, websocket: WebSocket) -> None:
        """Accept and register a WebSocket connection."""
        await websocket.accept()
        self._connections.add(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        self._connections.discard(websocket)

    async def send(
        self,
        websocket: WebSocket,
        message: Mapping[str, object],
    ) -> None:
        """Send one JSON message to one connected client."""
        await websocket.send_json(dict(message))

    async def broadcast(
        self,
        message: Mapping[str, object],
    ) -> None:
        """Send one JSON message to every active client."""
        disconnected: list[WebSocket] = []

        for websocket in tuple(self._connections):
            try:
                await self.send(websocket, message)
            except (RuntimeError, WebSocketDisconnect):
                disconnected.append(websocket)

        for websocket in disconnected:
            self.disconnect(websocket)
