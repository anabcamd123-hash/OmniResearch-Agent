from backend.agents.registry import registry
from backend.agents.reflection_agent import ReflectionAgent
from backend.executor.context import ExecutionContext
from backend.runtime.event_bus import event_bus
from backend.runtime.event_types import TASK_RETRY


class AutoFixExecutor:

    MAX_RETRY = 3

    def __init__(self):
        self.coder = registry.get("coding")
        self.verifier = registry.get("verify")
        self.reflector = ReflectionAgent()

    async def run(
        self,
        objective: str,
        context: ExecutionContext,
    ):

        code_result = await self.coder.run(
            objective, context
        )

        retry = 0

        while retry < self.MAX_RETRY:

            verify_result = await self.verifier.run(
                objective, context
            )

            if verify_result.success:
                return code_result

            reflection = await self.reflector.run(
                objective, context
            )

            if reflection.success:
                return code_result

            code_result = await self.coder.run(
                objective, context
            )

            retry += 1

            await event_bus.publish(
                TASK_RETRY,
                {
                    "task_id": objective,
                    "retry": retry,
                    "reason": reflection.content,
                },
            )

        raise Exception(
            f"AutoFix failed after "
            f"{self.MAX_RETRY} retries"
        )
