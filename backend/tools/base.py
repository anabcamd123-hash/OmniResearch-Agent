from abc import ABC, abstractmethod


class BaseTool(ABC):

    name: str
    description: str

    @abstractmethod
    async def run(self, input: str):
        pass
