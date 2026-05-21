from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class TaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskType(str, Enum):
    RESEARCH = "research"
    CODING = "coding"
    VERIFY = "verify"
    REFLECTION = "reflection"


class TaskModel(BaseModel):
    task_id: str
    task_type: TaskType
    status: TaskStatus = TaskStatus.PENDING
    dependencies: List[str] = []
    input_data: Optional[str] = None
    output_data: Optional[dict] = None
    retries: int = 0


class WorkflowModel(BaseModel):
    workflow_id: str
    status: TaskStatus = TaskStatus.PENDING
    tasks: List[TaskModel] = []
    created_at: Optional[str] = None


class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str
    tasks: List[dict]
