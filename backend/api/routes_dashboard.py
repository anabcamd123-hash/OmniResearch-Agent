from fastapi import APIRouter
from backend.runtime.runtime_state import state

router = APIRouter()

@router.get("/dashboard")

async def dashboard():

    return {
        "total_tasks": state.total_tasks,
        "completed_tasks": state.completed_tasks,
        "running_tasks": state.running_tasks,
        "token_usage": state.token_usage,
        "agents": state.agent_status
    }
