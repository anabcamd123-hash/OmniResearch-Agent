"""
Planner 输出 Schema

Pydantic 验证，防止 LLM 返回乱格式
"""

from pydantic import BaseModel
from typing import List


class PlanTask(BaseModel):
    id: str
    type: str
    depends: List[str] = []


class WorkflowPlan(BaseModel):
    tasks: List[PlanTask] = []
