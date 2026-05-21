from fastapi import APIRouter
from backend.runtime.runtime_state import state
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

    tasks = await task_repo.list_tasks(limit=1000)
    workflows = await workflow_repo.list_workflows(
        limit=100
    )

    total_tasks = len(tasks)
    completed_tasks = sum(
        1 for t in tasks if t.status == "completed"
    )
    running_tasks = sum(
        1 for t in tasks if t.status == "running"
    )

    token_usage = await token_repo.get_total()

    # Autofix stats from DB
    retry_tasks = sum(
        1
        for t in tasks
        if getattr(t, "retry_count", 0) > 0
    )

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "running_tasks": running_tasks,
        "token_usage": token_usage,
        "workflows": len(workflows),
        "agents": state.agent_status,
        "dag": state.current_dag,
        "timeline": state.timeline,
        "auto_fix": {
            "retried_tasks": retry_tasks,
        },
    }


@router.get("/autofix/stats")
async def autofix_stats():

    tasks = await task_repo.list_tasks(limit=1000)

    retry_tasks = sum(
        1
        for t in tasks
        if getattr(t, "retry_count", 0) > 0
    )

    return {
        "retried_tasks": retry_tasks,
    }
