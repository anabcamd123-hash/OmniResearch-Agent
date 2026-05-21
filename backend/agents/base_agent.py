from abc import ABC, abstractmethod
from backend.executor.context import ExecutionContext


class BaseAgent(ABC):

    @abstractmethod
    async def run(
        self,
        task: str,
        context: ExecutionContext,
    ):
        pass
