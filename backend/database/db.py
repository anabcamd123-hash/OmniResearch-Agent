import os
import json
import redis.asyncio as redis

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379")

_pool = None

async def get_redis():
    global _pool
    if _pool is None:
        _pool = redis.from_url(REDIS_URL, decode_responses=True)
    return _pool

async def save_task_result(task_id: str, result: dict):
    r = await get_redis()
    await r.set(f"task:{task_id}", json.dumps(result), ex=3600)

async def get_task_result(task_id: str):
    r = await get_redis()
    data = await r.get(f"task:{task_id}")
    return json.loads(data) if data else None

async def save_workflow(workflow_id: str, tasks: list):
    r = await get_redis()
    await r.set(f"workflow:{workflow_id}", json.dumps(tasks), ex=86400)

async def get_workflow(workflow_id: str):
    r = await get_redis()
    data = await r.get(f"workflow:{workflow_id}")
    return json.loads(data) if data else None

async def close_redis():
    global _pool
    if _pool:
        await _pool.close()
        _pool = None
