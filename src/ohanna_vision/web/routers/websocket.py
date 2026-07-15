"""WebSocket routes for Ohanna-Vision."""

from fastapi import APIRouter, WebSocket
from starlette.websockets import WebSocketDisconnect

from ohanna_vision.web.dependencies import WebSocketHubDependency

router = APIRouter(
    prefix="/ws",
    tags=["websocket"],
)


@router.websocket("")
async def websocket_endpoint(
    websocket: WebSocket,
    hub: WebSocketHubDependency,
) -> None:
    """Maintain a live Ohanna-Vision WebSocket connection."""
    await hub.connect(websocket)

    await hub.send(
        websocket,
        {
            "type": "connected",
            "message": "Ohanna Vision WebSocket connected",
        },
    )

    try:
        while True:
            message = await websocket.receive_json()

            if message.get("type") == "ping":
                await hub.send(
                    websocket,
                    {
                        "type": "pong",
                    },
                )
    except WebSocketDisconnect:
        hub.disconnect(websocket)
