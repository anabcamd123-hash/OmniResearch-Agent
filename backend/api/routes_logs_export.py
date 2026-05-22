"""
Logs Export API — CSV / JSON 导出（需登录）
"""

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
import io
import csv
import json

from backend.api.routes_auth import (
    get_current_user,
)
from backend.runtime.runtime_state import state

router = APIRouter(
    prefix="/export", tags=["export"]
)


@router.get("/history/csv")
async def export_history_csv(
    current_user=Depends(get_current_user),
):
    """导出 timeline 为 CSV"""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["agent", "event", "task_id"]
    )
    for record in state.timeline:
        writer.writerow(
            [
                record.get("agent", ""),
                record.get("event", ""),
                record.get("task_id", ""),
            ]
        )
    output.seek(0)
    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=task_history.csv"
            )
        },
    )


@router.get("/history/json")
async def export_history_json(
    current_user=Depends(get_current_user),
):
    """导出 timeline 为 JSON"""
    data = json.dumps(
        state.timeline, indent=2
    )
    return StreamingResponse(
        io.BytesIO(data.encode()),
        media_type="application/json",
        headers={
            "Content-Disposition": (
                "attachment; "
                "filename=task_history.json"
            )
        },
    )
