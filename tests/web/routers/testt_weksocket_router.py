"""Tests for the Ohanna-Vision WebSocket router."""

from fastapi.testclient import TestClient

from ohanna_vision.web import WebSocketHub, create_app


def test_websocket_router_accepts_connection() -> None:
    """The WebSocket endpoint must accept a client."""
    hub = WebSocketHub()
    client = TestClient(
        create_app(websocket_hub=hub),
    )

    with client.websocket_connect("/ws") as websocket:
        message = websocket.receive_json()

        assert message == {
            "type": "connected",
            "message": "Ohanna Vision WebSocket connected",
        }
        assert hub.connection_count == 1

    assert hub.connection_count == 0


def test_websocket_router_answers_ping() -> None:
    """The WebSocket endpoint must answer application pings."""
    client = TestClient(create_app())

    with client.websocket_connect("/ws") as websocket:
        websocket.receive_json()

        websocket.send_json(
            {
                "type": "ping",
            }
        )

        assert websocket.receive_json() == {
            "type": "pong",
        }


def test_websocket_router_ignores_unknown_messages() -> None:
    """Unknown message types must not close the connection."""
    hub = WebSocketHub()
    client = TestClient(
        create_app(websocket_hub=hub),
    )

    with client.websocket_connect("/ws") as websocket:
        websocket.receive_json()

        websocket.send_json(
            {
                "type": "unknown",
            }
        )

        assert hub.connection_count == 1
