"""
Dashboard WebSocket — 认证 + 实时推送 + 控制命令

Viewer: 只接收
Admin: 可发送命令 (start:xxx)
"""

import asyncio
import json

from fastapi import (
    APIRouter,
    WebSocket,
    WebSocketDisconnect,
)
from backend.runtime.runtime_state import state
from backend.api.routes_auth import verify_token
from backend.executor.workflow_executor import WorkflowExecutor
workflow_executor = WorkflowExecutor()
from backend.storage.audit_repository import audit_repo
from backend.utils.logger import logger

router = APIRouter()

connections: dict = {}


async def broadcast(message: str):
    """广播消息给所有连接"""
    for ws in list(connections):
        try:
            await ws.send_text(message)
        except Exception:
            connections.pop(ws, None)


@router.websocket("/ws/dashboard")
async def dashboard_ws(websocket: WebSocket):
    # 从 query param 获取 token
    token = websocket.query_params.get(
        "access_token", ""
    )

    user = {"sub": "anonymous", "role": "viewer"}
    if token:
        try:
            user = verify_token(token)
        except Exception:
            pass

    await websocket.accept()
    connections[websocket] = user
    logger.info(
        f"[WS] Connected: {user.get('sub')} "
        f"({user.get('role')})"
    )

    try:
        while True:
            # 非阻塞：同时推送状态和接收命令
            try:
                data = await asyncio.wait_for(
                    websocket.receive_text(),
                    timeout=1.0,
                )
                # 收到命令
                if user.get("role") != "admin":
                    await websocket.send_text(
                        json.dumps(
                            {
                                "log": (
                                    "[WS] Denied: "
                                    "admin only"
                                )
                            }
                        )
                    )
                    continue

                # 处理 admin 命令
                # 审计记录
                await audit_repo.add_log(
                    user=user.get("sub", "unknown"),
                    role=user.get("role", "unknown"),
                    action="ws_command",
                    target=data[:200],
                )

                if data.startswith("start:"):
                    task_desc = data[
                        len("start:") :
                    ].strip()
                    asyncio.create_task(
                        workflow_executor.execute(
                            task_desc
                        )
                    )
                    await websocket.send_text(
                        json.dumps(
                            {
                                "log": (
                                    f"[WS] Started: "
                                    f"{task_desc[:50]}"
                                )
                            }
                        )
                    )
                else:
                    await websocket.send_text(
                        json.dumps(
                            {
                                "log": (
                                    f"[WS] Unknown: "
                                    f"{data}"
                                )
                            }
                        )
                    )

            except asyncio.TimeoutError:
                # 超时 = 无命令，继续推送状态
                pass

            # 推送实时状态
            message = json.dumps(
                {
                    "timeline": state.timeline[
                        -50:
                    ],
                    "agent_status": (
                        state.agent_status
                    ),
                    "current_dag": (
                        state.current_dag
                    ),
                    "auto_fix_stats": (
                        state.auto_fix_stats
                    ),
                }
            )
            await websocket.send_text(message)

    except (WebSocketDisconnect, Exception):
        connections.pop(websocket, None)
        logger.info(
            f"[WS] Disconnected: "
            f"{user.get('sub')}"
        )
