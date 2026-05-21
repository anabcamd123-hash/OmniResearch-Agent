from backend.agents.registry import registry
from backend.agents.reflection_agent import ReflectionAgent
from backend.utils.logger import stream_log
from backend.runtime.events import bus


class ToolLoopExecutor:

    def __init__(self):

        self.registry = registry

        self.reflector = ReflectionAgent()

        self.max_retry = 3

    async def run(
        self,
        task: str,
        agent_type: str = "research",
        context=None,
    ):

        await stream_log(
            f"[ToolLoop] {agent_type}: "
            f"{task[:50]}"
        )

        agent = self.registry.get(agent_type)

        retry = 0

        last_result = None

        while retry < self.max_retry:

            # 1. Execute agent
            if context and agent_type != "research":
                payload = context
            else:
                payload = task

            result = await agent.run(payload)

            last_result = result

            # 2. Check success
            if result.success:
                await stream_log(
                    f"[ToolLoop] Success after "
                    f"{retry} retries"
                )
                return {
                    "result": result,
                    "retry": retry,
                    "status": "completed",
                }

            # 3. Reflect
            reflection = await self.reflector.run(
                task, str(result.to_dict())
            )

            # 4. Check reflection
            if reflection.success:
                await stream_log(
                    f"[ToolLoop] Accepted after "
                    f"{retry} retries"
                )
                return {
                    "result": result,
                    "retry": retry,
                    "status": "completed",
                }

            # 5. Retry with context
            await stream_log(
                f"[ToolLoop] Retry {retry + 1}: "
                f"{reflection.content[:50]}"
            )

            await bus.publish("task_retry", {
                "task": task,
                "retry": retry + 1,
                "reason": reflection.content,
            })

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
