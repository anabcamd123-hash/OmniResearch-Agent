from backend.agents.registry import registry
from backend.agents.reflection_agent import ReflectionAgent
from backend.executor.context import ExecutionContext
from backend.utils.logger import stream_log
from backend.runtime.events import bus


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

        await stream_log(
            f"[AutoFix] Starting: "
            f"{objective[:50]}..."
        )

        code_result = await self.coder.run(
            objective, context
        )

        retry = 0

        while retry < self.MAX_RETRY:

            verify_result = await self.verifier.run(
                objective, context
            )

            if verify_result.success:
                await stream_log(
                    f"[AutoFix] Success after "
                    f"{retry} retries"
                )
                return code_result

            await stream_log(
                f"[AutoFix] Failed, retry "
                f"{retry + 1}"
            )

            reflection = await self.reflector.run(
                objective, context
            )

            if reflection.success:
                return code_result

            code_result = await self.coder.run(
                objective, context
            )

            await bus.publish("autofix_retry", {
                "objective": objective,
                "retry": retry + 1,
                "reason": reflection.content,
            })

            retry += 1

        raise Exception(
            f"AutoFix failed after "
            f"{self.MAX_RETRY} retries"
        )
