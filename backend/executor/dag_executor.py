import time
import asyncio
from backend.executor.task_graph import TaskGraph
from backend.executor.tool_loop_executor import ToolLoopExecutor
from backend.executor.context import ExecutionContext
from backend.agents.registry import registry
from backend.utils.logger import stream_log
from backend.runtime.runtime_state import state
from backend.runtime.events import bus


class DAGExecutor:
    def __init__(self):
        self.completed_tasks = set()
        self.tool_loop = ToolLoopExecutor()
        self.context = ExecutionContext()

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

        # Get previous context
        prev_result = None
        if task.dependencies:
            prev_key = task.dependencies[-1]
            prev_result = self.context.get(
                prev_key
            )

        # Execute via tool loop
        result = await self.tool_loop.run(
            task=task.task_id,
            agent_type=task.task_type,
            context=prev_result,
        )

        task.end_time = time.time()
        task.duration = (
            task.end_time - task.start_time
        )
        task.status = result["status"]
        self.completed_tasks.add(task.task_id)

        # Store result in context
        self.context.set(
            task.task_id,
            result.get("result"),
        )

        await stream_log(
            f"[Executor] {task.task_id}: "
            f"{result['status']} "
            f"(retries={result['retry']})"
        )

        state.timeline.append({
            "agent": task.task_type.capitalize(),
            "event": result["status"],
        })

        await bus.publish("task_completed", {
            "task_id": task.task_id,
            "status": result["status"],
            "retry": result["retry"],
        })
