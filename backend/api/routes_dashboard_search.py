"""
Dashboard Search — 搜索 Workflow & Task
"""

from fastapi import APIRouter, Query

from backend.storage.repository import (
    WorkflowRepository,
    TaskRepository,
)

router = APIRouter(
    prefix="/dashboard", tags=["dashboard-search"]
)

workflow_repo = WorkflowRepository()
task_repo = TaskRepository()


@router.get("/search/workflows")
async def search_workflows(
    keyword: str = Query(...),
):
    """搜索 workflow（按 objective 或 workflow_id）"""
    results = await workflow_repo.search_workflows(
        keyword
    )
    return {"results": results}


@router.get("/search/tasks")
async def search_tasks(
    keyword: str = Query(...),
):
    """搜索 task（按 objective 或 task_id）"""
    results = await task_repo.search_tasks(keyword)
    return {"results": results}
