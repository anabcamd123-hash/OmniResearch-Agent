"""
StateRepository — 状态存储抽象接口
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
