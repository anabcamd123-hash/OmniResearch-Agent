from fastapi import APIRouter
from backend.runtime.workflow_state import workflow_state
from backend.runtime.task_queue import task_queue
from backend.runtime.task_state import task_state
from backend.executor.dag_executor import DAGExecutor

router = APIRouter()


@router.get("/workflow/{workflow_id}")
async def get_workflow(workflow_id: str):

    state = workflow_state.load(workflow_id)

    if not state:
        return {"error": "Workflow not found"}

    return state


@router.get("/workflows/running")
async def list_running():

    return workflow_state.list_running()


@router.post("/workflow/{workflow_id}/resume")
async def resume_workflow(workflow_id: str):

    executor = DAGExecutor()

    await executor.resume_workflow(
        workflow_id
    )

    return {
        "status": "resumed",
        "workflow_id": workflow_id,
    }


@router.get("/queue/status")
async def queue_status():

    return {
        "queue_size": task_queue.size(),
    }
