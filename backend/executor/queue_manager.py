import aioredis
import asyncio

redis = aioredis.from_url("redis://localhost")

async def enqueue_task(task_data):
    await redis.rpush("task_queue", task_data)

async def dequeue_task():
    data = await redis.lpop("task_queue")
    return data
