from fastapi import APIRouter
from backend.runtime.task_history import history

router = APIRouter()

@router.get("/history")
async def get_history():

    return history.records
