"""
RedisStateRepository — Redis 状态存储
"""

import redis
from backend.storage.state_repository import StateRepository
from backend.config.settings import settings


class RedisStateRepository(StateRepository):

    def __init__(self):
        self.client = redis.Redis.from_url(
            settings.REDIS_URL, decode_responses=True
        )

    async def get(self, key: str):
        return self.client.get(key)

    async def set(self, key: str, value):
        self.client.set(key, str(value))

    async def delete(self, key: str):
        self.client.delete(key)
