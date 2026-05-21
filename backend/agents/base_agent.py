from abc import ABC, abstractmethod
from time import perf_counter
from backend.executor.context import ExecutionContext
from backend.agents.result import AgentResult


class BaseAgent(ABC):

    name = "base"

    async def execute(
        self,
        task: str,
        context: ExecutionContext,
    ) -> dict:

        start = perf_counter()

        try:

            result = await self.run(
                task,
                context,
            )

            duration = perf_counter() - start

            return {
                "success": True,
                "duration": duration,
                "result": result,
            }

        except Exception as e:

            duration = perf_counter() - start

            return {
                "success": False,
                "duration": duration,
                "error": str(e),
            }

    @abstractmethod
    async def run(
        self,
        task: str,
        context: ExecutionContext,
    ) -> AgentResult:
        pass
