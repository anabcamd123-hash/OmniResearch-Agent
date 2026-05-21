from fastapi import APIRouter
from backend.database.db import (
    get_all_tasks, get_all_workflows
)

router = APIRouter()


@router.get("/db/tasks")
async def db_tasks():

    return get_all_tasks()


@router.get("/db/workflows")
async def db_workflows():

    return get_all_workflows()
