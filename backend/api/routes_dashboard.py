from fastapi import APIRouter
from backend.storage.repository import (
    TaskRepository,
    WorkflowRepository,
    TokenRepository,
)

router = APIRouter()

task_repo = TaskRepository()
workflow_repo = WorkflowRepository()
token_repo = TokenRepository()


@router.get("/dashboard")
async def dashboard():

    # All metrics from SQLite
    tasks = await task_repo.list_tasks(limit=1000)
    workflows = await workflow_repo.list_workflows(limit=100)

    total_tasks = len(tasks)
    completed_tasks = sum(
        1 for t in tasks if t.status == "completed"
    )
    running_tasks = sum(
        1 for t in tasks if t.status == "running"
    )

    token_usage = await token_repo.get_total()

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "running_tasks": running_tasks,
        "token_usage": token_usage,
        "workflows": len(workflows),
    }
