from fastapi import APIRouter, WebSocket

from backend.api.ws_manager import manager

router = APIRouter()

@router.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):

    await manager.connect(websocket)

    try:
        while True:
            await websocket.receive_text()

    except:
        manager.disconnect(websocket)
