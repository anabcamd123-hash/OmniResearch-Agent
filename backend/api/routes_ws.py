"""
WebSocket 路由 — 简洁广播
"""

import asyncio
import json

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from backend.runtime.runtime_state import state

router = APIRouter()

connections: list[WebSocket] = []


async def broadcast(message: str):
    """广播消息给所有连接的客户端"""
    for conn in list(connections):
        try:
            await conn.send_text(message)
        except Exception:
            connections.remove(conn)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
):
    await websocket.accept()
    connections.append(websocket)
    try:
        while True:
            # 推送状态快照
            await asyncio.sleep(1)
            snapshot = json.dumps({
                "type": "state_update",
                "agent_status": state.agent_status,
                "current_dag": state.current_dag,
            })
            await broadcast(snapshot)
    except (WebSocketDisconnect, Exception):
        if websocket in connections:
            connections.remove(websocket)
