"""
Task Logs API — 单任务执行日志
"""

from fastapi import APIRouter

from backend.storage.repository import TaskRepository

router = APIRouter(
    prefix="/tasks", tags=["task-logs"]
)

task_repo = TaskRepository()


@router.get("/{task_id}/log")
async def get_task_log(task_id: str):
    """获取单个任务详细执行日志"""
    task = await task_repo.get_task(task_id)
    if not task:
        return {
            "status": "error",
            "message": "Task not found",
        }

    return {
        "task_id": task.task_id,
        "objective": task.objective,
        "status": task.status,
        "duration": task.duration or 0,
        "result": task.result or "",
        "retry": getattr(
            task, "retry_count", 0
        ),
    }
