"""
Executor API - 任务提交、状态查询、DLQ 查看
"""

from fastapi import APIRouter
from pydantic import BaseModel

from backend.executor.workflow_executor import WorkflowExecutor
from backend.runtime.dlq import dlq_list
from backend.storage.repository import (
    WorkflowRepository,
)
from backend.utils.logger import logger

router = APIRouter(
    prefix="/executor", tags=["executor"]
)

workflow_repo = WorkflowRepository()


class SubmitRequest(BaseModel):
    task: str


@router.post("/submit")
async def submit_workflow(req: SubmitRequest):
    """提交一个工作流任务"""
    logger.info(
        f"[API] Submit: {req.task[:50]}"
    )
    result = await workflow_executor.execute(
        req.task
    )
    return {
        "status": "success",
        "workflow": result,
    }


@router.get("/status/{workflow_id}")
async def workflow_status(workflow_id: str):
    """查询 workflow 状态"""
    workflows = (
        await workflow_repo.list_workflows(
            limit=100
        )
    )
    for wf in workflows:
        if wf.workflow_id == workflow_id:
            return {
                "workflow_id": wf.workflow_id,
                "status": wf.status,
                "total_tasks": wf.total_tasks,
                "completed_tasks": (
                    wf.completed_tasks
                ),
                "objective": wf.objective,
            }
    return {"error": "Workflow not found"}


@router.get("/dlq")
async def dlq_tasks():
    """查看当前 DLQ 中未完成任务"""
    tasks = await dlq_list()
    return {
        "dlq_count": len(tasks),
        "tasks": tasks,
    }
