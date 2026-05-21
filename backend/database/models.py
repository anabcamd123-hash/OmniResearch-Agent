from sqlalchemy import Column, String, Integer
from sqlalchemy.ext.declarative import declarative_base
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum

# SQLAlchemy models
Base = declarative_base()

class TaskRecord(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(String, unique=True)
    status = Column(String)
    retries = Column(Integer, default=0)

# Pydantic models
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
