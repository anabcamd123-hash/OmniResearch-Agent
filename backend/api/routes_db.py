from fastapi import APIRouter
from backend.storage.repository import (
    TaskRepository,
    WorkflowRepository,
    LogRepository,
)

router = APIRouter()

task_repo = TaskRepository()
workflow_repo = WorkflowRepository()
log_repo = LogRepository()


@router.get("/tasks")
async def list_tasks():

    tasks = await task_repo.list_tasks()

    return [
        {
            "task_id": t.task_id,
            "objective": t.objective,
            "status": t.status,
            "result": t.result,
            "duration": t.duration,
            "created_at": str(t.created_at),
        }
        for t in tasks
    ]


@router.get("/task/{task_id}")
async def get_task(task_id: str):

    task = await task_repo.get_task(task_id)

    if not task:
        return {"error": "Task not found"}

    return {
        "task_id": task.task_id,
        "objective": task.objective,
        "status": task.status,
        "result": task.result,
        "duration": task.duration,
        "created_at": str(task.created_at),
    }


@router.get("/workflows")
async def list_workflows():

    workflows = await workflow_repo.list_workflows()

    return [
        {
            "workflow_id": w.workflow_id,
            "objective": w.objective,
            "status": w.status,
            "total_tasks": w.total_tasks,
            "completed_tasks": w.completed_tasks,
            "token_usage": w.token_usage,
            "created_at": str(w.created_at),
        }
        for w in workflows
    ]


@router.get("/logs")
async def list_logs():

    logs = await log_repo.list_logs()

    return [
        {
            "message": l.message,
            "level": l.level,
            "created_at": str(l.created_at),
        }
        for l in logs
    ]
