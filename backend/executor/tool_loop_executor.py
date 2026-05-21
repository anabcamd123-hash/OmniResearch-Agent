from backend.tools.router import tool_router
from backend.agents.reflection_agent import ReflectionAgent
from backend.utils.logger import stream_log


class ToolLoopExecutor:

    def __init__(self):

        self.router = tool_router

        self.reflector = ReflectionAgent()

        self.max_retry = 3

    async def run(self, task: str):

        await stream_log(
            f"[ToolLoop] Starting: {task[:50]}"
        )

        retry = 0

        last_result = None

        while retry < self.max_retry:

            # 1. Execute tool
            result = await self.router.execute(task)

            last_result = result

            # 2. Reflect
            reflection = await self.reflector.run(
                task, result
            )

            # 3. Success → exit
            if not reflection.need_retry:

                await stream_log(
                    f"[ToolLoop] Success after "
                    f"{retry} retries"
                )

                return {
                    "result": result,
                    "retry": retry,
                    "status": "completed",
                }

            # 4. Retry with context
            await stream_log(
                f"[ToolLoop] Retry {retry + 1}: "
                f"{reflection.reason[:50]}"
            )

            task = (
                f"Original task: {task}\n"
                f"Previous failure: "
                f"{reflection.reason}\n"
                f"Fix and retry."
            )

            retry += 1

        await stream_log(
            f"[ToolLoop] Failed after "
            f"{self.max_retry} retries"
        )

        return {
            "result": last_result,
            "retry": retry,
            "status": "failed",
        }


tool_loop_executor = ToolLoopExecutor()
