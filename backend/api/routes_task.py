from fastapi import APIRouter
from pydantic import BaseModel

from backend.agents.planner_agent import PlannerAgent

router = APIRouter()

planner = PlannerAgent()

class TaskRequest(BaseModel):
    task: str

@router.post("/task")
async def create_task(req: TaskRequest):

    plan = planner.create_plan(req.task)

    return {
        "success": True,
        "plan": plan
    }
