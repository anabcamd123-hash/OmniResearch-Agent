from backend.agents.registry import registry
from backend.agents.reflection_agent import ReflectionAgent
from backend.executor.context import ExecutionContext
from backend.runtime.event_bus import event_bus
from backend.runtime.event_types import (
    TASK_STARTED,
    TASK_COMPLETED,
    TASK_FAILED,
    TASK_RETRY,
)


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

        if not context:
            context = ExecutionContext()

        agent = self.registry.get(agent_type)

        retry = 0

        last_result = None

        while retry < self.max_retry:

            result = await agent.run(task, context)

            last_result = result

            if result.success:
                return {
                    "result": result,
                    "retry": retry,
                    "status": "completed",
                }

            reflection = await self.reflector.run(
                task, context
            )

            if reflection.success:
                return {
                    "result": result,
                    "retry": retry,
                    "status": "completed",
                }

            retry += 1

            await event_bus.publish(
                TASK_RETRY,
                {
                    "task_id": task,
                    "retry": retry,
                    "reason": reflection.content,
                },
            )

        return {
            "result": last_result,
            "retry": retry,
            "status": "failed",
        }


tool_loop_executor = ToolLoopExecutor()
