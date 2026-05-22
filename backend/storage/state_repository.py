"""
StateRepository — 状态存储抽象接口

三种后端自动降级：Redis → SQLite → Memory
"""

from abc import ABC, abstractmethod


class StateRepository(ABC):

    @abstractmethod
    async def get(self, key: str):
        pass

    @abstractmethod
    async def set(self, key: str, value):
        pass

    @abstractmethod
    async def delete(self, key: str):
        pass
