from fastapi import APIRouter
from pydantic import BaseModel

from backend.executor.workflow_executor import WorkflowExecutor

router = APIRouter()

executor = WorkflowExecutor()

class TaskRequest(BaseModel):
    task: str

@router.post("/task")
async def create_task(req: TaskRequest):

    result = await executor.execute(req.task)

    return {
        "success": True,
        "workflow": result
    }
