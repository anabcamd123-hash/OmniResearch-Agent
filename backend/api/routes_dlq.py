"""
DLQ API
"""

from fastapi import APIRouter
from backend.runtime.dlq import dlq_list, dlq_pop, dlq_count, dlq_remove

router = APIRouter(tags=["dlq"])


@router.get("/dlq")
async def get_dlq():
    items = await dlq_list()
    return {"count": await dlq_count(), "items": items}


@router.post("/dlq/retry")
async def retry_one():
    task = await dlq_pop()
    if not task:
        return {"success": False, "message": "DLQ is empty"}
    return {"success": True, "task": task}


@router.delete("/dlq/clear")
async def clear_dlq():
    items = await dlq_list(limit=1000)
    for item in items:
        await dlq_remove(item["task_id"])
    return {"success": True, "cleared": len(items)}
