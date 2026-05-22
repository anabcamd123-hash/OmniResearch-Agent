"""
Workflow API
"""

from fastapi import APIRouter

from backend.runtime.workflow_state import (
    workflow_state,
)
from backend.runtime.task_queue import task_queue
from backend.executor.dag_executor import DAGExecutor

router = APIRouter()


@router.get("/workflow/{workflow_id}")
async def get_workflow(workflow_id: str):
    """查看 workflow 详情（含 per-task 状态）"""
    state = workflow_state.load(workflow_id)
    if not state:
        return {"error": "Workflow not found"}
    return state


@router.get("/workflows/running")
async def list_running():
    """列出所有 running workflows"""
    return workflow_state.list_running()


@router.post("/workflow/{workflow_id}/resume")
async def resume_workflow(workflow_id: str):
    """手动触发 workflow 恢复"""
    wf_data = workflow_state.load(workflow_id)
    if not wf_data:
        return {"error": "Workflow not found"}

    executor = DAGExecutor()
    await executor.resume_workflow(wf_data)

    return {
        "status": "resumed",
        "workflow_id": workflow_id,
    }


@router.get("/workflow/{workflow_id}/tasks")
async def get_workflow_tasks(workflow_id: str):
    """查看 workflow 下所有 task 状态"""
    state = workflow_state.load(workflow_id)
    if not state:
        return {"error": "Workflow not found"}

    tasks = state.get("tasks", {})
    summary = {}
    for tid, info in tasks.items():
        status = (
            info["status"]
            if isinstance(info, dict)
            else info
        )
        summary[status] = (
            summary.get(status, 0) + 1
        )

    return {
        "workflow_id": workflow_id,
        "status": state.get("status"),
        "total": len(tasks),
        "summary": summary,
        "tasks": tasks,
    }


@router.get("/queue/status")
async def queue_status():
    """队列状态"""
    return {
        "queue_size": task_queue.size(),
    }
