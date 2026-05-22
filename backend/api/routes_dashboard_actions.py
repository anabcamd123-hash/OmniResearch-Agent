"""
Dashboard Actions — DLQ 操作 + 历史查询
"""

from fastapi import APIRouter

from backend.runtime.dlq import dlq_list, dlq_remove
from backend.storage.repository import (
    WorkflowRepository,
)

from backend.utils.logger import logger

router = APIRouter(
    prefix="/dashboard", tags=["dashboard"]
)

workflow_repo = WorkflowRepository()


@router.get("/dlq")
async def get_dlq_tasks():
    """获取当前 DLQ 任务"""
    tasks = await dlq_list()
    return {
        "dlq_count": len(tasks),
        "tasks": tasks,
    }


@router.post("/dlq/retry/{task_id}")
async def retry_dlq_task(task_id: str):
    """手动重试 DLQ 中的任务"""
    # 查找任务
    tasks = await dlq_list(limit=1000)
    task = next(
        (
            t
            for t in tasks
            if t["task_id"] == task_id
        ),
        None,
    )

    if not task:
        return {
            "status": "error",
            "message": "Task not found in DLQ",
        }

    # 从 DLQ 移除
    await dlq_repo.remove_task(task_id)

    return {
        "status": "success",
        "task_id": task_id,
        "message": "Task removed from DLQ. Use executor to retry.",
    }


@router.get("/history")
async def get_workflow_history(
    limit: int = 10,
):
    """获取最近 workflow 历史"""
    workflows = await workflow_repo.list_workflows(
        limit=limit
    )
    return {
        "workflows": [
            {
                "workflow_id": wf.workflow_id,
                "status": wf.status,
                "objective": wf.objective,
                "total_tasks": wf.total_tasks,
                "completed_tasks": (
                    wf.completed_tasks
                ),
                "created_at": str(
                    wf.created_at
                ),
            }
            for wf in workflows
        ]
    }
