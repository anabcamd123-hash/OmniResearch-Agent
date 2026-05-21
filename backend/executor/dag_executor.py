import time
import asyncio
from backend.executor.task_graph import TaskGraph
from backend.executor.context import ExecutionContext
from backend.agents.registry import registry
from backend.agents.reflection_agent import ReflectionAgent
from backend.runtime.event_bus import event_bus
from backend.runtime.event_types import (
    TASK_STARTED,
    TASK_COMPLETED,
    TASK_FAILED,
    TASK_RETRY,
)
from backend.runtime.agent_stats import agent_stats


class DAGExecutor:
    def __init__(self):
        self.completed_tasks = set()
        self.registry = registry
        self.context = ExecutionContext()
        self.reflector = ReflectionAgent()
        self.max_retry = 3

    async def execute(self, tasks):
        graph = TaskGraph()
        for task in tasks:
            graph.add_task(task)

        self.context.clear()

        while len(self.completed_tasks) < len(tasks):
            ready_tasks = graph.get_ready_tasks(
                self.completed_tasks
            )
            if not ready_tasks:
                break
            await asyncio.gather(
                *[
                    self.run_task(task)
                    for task in ready_tasks
                ]
            )

    async def run_task(self, task):
        task.status = "running"
        task.start_time = time.time()

        await event_bus.publish(
            TASK_STARTED,
            {
                "task_id": task.task_id,
                "task_type": task.task_type,
            },
        )

        agent = self.registry.get(
            task.task_type
        )

        retry = 0

        while retry < self.max_retry:

            result = await agent.run(
                task.task_id,
                self.context,
            )

            if result.success:
                task.result = result
                task.end_time = time.time()
                task.duration = (
                    task.end_time - task.start_time
                )
                task.status = "completed"
                self.completed_tasks.add(
                    task.task_id
                )

                # Agent stats
                agent_stats.record(
                    task.task_type,
                    task.duration,
                )

                await event_bus.publish(
                    TASK_COMPLETED,
                    {
                        "task_id": task.task_id,
                        "task_type": task.task_type,
                        "duration": task.duration,
                    },
                )

                return

            reflection = await self.reflector.run(
                task.task_id, self.context
            )

            if reflection.success:
                task.result = result
                task.end_time = time.time()
                task.duration = (
                    task.end_time - task.start_time
                )
                task.status = "completed"
                self.completed_tasks.add(
                    task.task_id
                )

                agent_stats.record(
                    task.task_type,
                    task.duration,
                )

                await event_bus.publish(
                    TASK_COMPLETED,
                    {
                        "task_id": task.task_id,
                        "task_type": task.task_type,
                        "duration": task.duration,
                    },
                )

                return

            retry += 1

            await event_bus.publish(
                TASK_RETRY,
                {
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "retry": retry,
                    "reason": reflection.content,
                },
            )

        # Max retries exceeded
        task.result = result
        task.end_time = time.time()
        task.duration = (
            task.end_time - task.start_time
        )
        task.status = "failed"
        self.completed_tasks.add(task.task_id)

        agent_stats.record(
            task.task_type,
            task.duration,
        )

        await event_bus.publish(
            TASK_FAILED,
            {
                "task_id": task.task_id,
                "task_type": task.task_type,
                "duration": task.duration,
            },
        )
