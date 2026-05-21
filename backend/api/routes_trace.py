from fastapi import APIRouter
from backend.runtime.trace_store import trace_store

router = APIRouter()


@router.get("/trace")
async def get_trace():

    return trace_store.recent(200)
