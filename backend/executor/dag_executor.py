import time
import asyncio
from backend.executor.task_graph import TaskGraph
from backend.executor.context import ExecutionContext
from backend.agents.registry import registry
from backend.agents.reflection_agent import ReflectionAgent
from backend.utils.logger import stream_log
from backend.runtime.runtime_state import state
from backend.runtime.events import bus


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
        await stream_log(
            f"[Executor] Running: {task.task_id}"
        )

        state.timeline.append({
            "agent": task.task_type.capitalize(),
            "event": "started",
        })

        await bus.publish("task_started", {
            "task_id": task.task_id,
            "task_type": task.task_type,
        })

        # Get agent from registry
        agent = self.registry.get(
            task.task_type
        )

        retry = 0

        while retry < self.max_retry:

            # Execute agent
            result = await agent.run(
                task.task_id,
                self.context,
            )

            # Check success
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

                await stream_log(
                    f"[Executor] Completed: "
                    f"{task.task_id}"
                )

                state.timeline.append({
                    "agent": task.task_type.capitalize(),
                    "event": "completed",
                })

                await bus.publish("task_completed", {
                    "task_id": task.task_id,
                    "status": "completed",
                })

                return

            # Failed → reflect
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

                await stream_log(
                    f"[Executor] Accepted: "
                    f"{task.task_id}"
                )

                state.timeline.append({
                    "agent": task.task_type.capitalize(),
                    "event": "completed",
                })

                await bus.publish("task_completed", {
                    "task_id": task.task_id,
                    "status": "completed",
                })

                return

            # Retry
            retry += 1
            await stream_log(
                f"[Executor] Retry {retry}: "
                f"{task.task_id}"
            )

            await bus.publish("task_retry", {
                "task_id": task.task_id,
                "retry": retry,
                "reason": reflection.content,
            })

        # Max retries exceeded
        task.result = result
        task.end_time = time.time()
        task.duration = (
            task.end_time - task.start_time
        )
        task.status = "failed"
        self.completed_tasks.add(task.task_id)

        await stream_log(
            f"[Executor] Failed: {task.task_id}"
        )

        state.timeline.append({
            "agent": task.task_type.capitalize(),
            "event": "failed",
        })

        await bus.publish("task_completed", {
            "task_id": task.task_id,
            "status": "failed",
        })
