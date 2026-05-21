from fastapi import APIRouter
from backend.memory.memory_store import memory

router = APIRouter()


@router.get("/memory")
async def get_memory():

    memories = await memory.get_recent(limit=20)

    return {"memories": memories}


@router.delete("/memory")
async def clear_memory():

    await memory.clear()

    return {"status": "cleared"}
