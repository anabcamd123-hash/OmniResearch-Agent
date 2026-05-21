from fastapi import APIRouter
from backend.storage.repository import TaskRepository

router = APIRouter()

task_repo = TaskRepository()


@router.get("/history")
async def get_history():

    tasks = await task_repo.list_tasks(limit=50)

    return [
        {
            "task": t.task_id,
            "status": t.status,
            "duration": t.duration,
            "time": str(t.created_at),
        }
        for t in tasks
    ]
