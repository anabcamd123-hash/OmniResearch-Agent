"""
MemStateRepository — 内存状态存储（降级兜底）
"""

from backend.storage.state_repository import (
    StateRepository,
)


class MemStateRepository(StateRepository):

    def __init__(self):
        self.store: dict = {}

    async def get(self, key: str):
        return self.store.get(key)

    async def set(self, key: str, value):
        self.store[key] = value

    async def delete(self, key: str):
        self.store.pop(key, None)
