"""
WebSocket 后端 — 推送 workflow 状态

每秒推送 timeline + DAG
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

clients: set = set()


async def broadcast(message: str):
    """广播字符串消息"""
    for conn in list(clients):
        try:
            await conn.send_text(message)
        except Exception:
            clients.discard(conn)


@router.websocket("/ws/workflows")
async def workflow_ws(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await asyncio.sleep(1)
            data = {
                "timeline": state.timeline[-50:],
                "current_dag": state.current_dag,
                "agent_status": state.agent_status,
            }
            dead = set()
            for client in clients:
                try:
                    await client.send_json(data)
                except Exception:
                    dead.add(client)
            clients.difference_update(dead)
    except Exception:
        clients.discard(ws)


@router.websocket("/ws")
async def legacy_ws(ws: WebSocket):
    """兼容旧路径"""
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            await ws.receive_text()
    except (WebSocketDisconnect, Exception):
        clients.discard(ws)
