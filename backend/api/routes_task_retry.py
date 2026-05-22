"""
Task Retry API — 仅 admin 可用
"""

from fastapi import APIRouter, Depends

from backend.utils.permissions import (
    require_role,
)
from backend.storage.repository import (
    TaskRepository,
)
from backend.utils.logger import logger

router = APIRouter(
    prefix="/tasks", tags=["tasks"]
)

task_repo = TaskRepository()


@router.post("/retry/{task_id}")
async def retry_task(
    task_id: str,
    current_user=Depends(
        require_role("admin")
    ),
):
    """仅 admin 可以重试任务"""
    task = await task_repo.get_task(task_id)
    if not task:
        return {"error": "Task not found"}

    await task_repo.update_status(
        task_id, "pending"
    )

    logger.info(
        f"[Admin] {current_user['sub']} "
        f"retried {task_id}"
    )

    return {
        "message": (
            f"Task {task_id} "
            f"marked for retry"
        ),
    }
