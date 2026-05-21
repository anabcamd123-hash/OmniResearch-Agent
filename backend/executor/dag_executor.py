import time
import asyncio
from backend.executor.task_graph import TaskGraph
from backend.executor.tool_loop_executor import ToolLoopExecutor
from backend.utils.logger import stream_log
from backend.runtime.runtime_state import state


class DAGExecutor:
    def __init__(self):
        self.completed_tasks = set()
        self.tool_loop = ToolLoopExecutor()

    async def execute(self, tasks):
        graph = TaskGraph()
        for task in tasks:
            graph.add_task(task)

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

        result = await self.tool_loop.run(
            task.task_id
        )

        task.end_time = time.time()
        task.duration = (
            task.end_time - task.start_time
        )
        task.status = result["status"]
        self.completed_tasks.add(task.task_id)

        await stream_log(
            f"[Executor] {task.task_id}: "
            f"{result['status']} "
            f"(retries={result['retry']})"
        )

        state.timeline.append({
            "agent": task.task_type.capitalize(),
            "event": result["status"],
        })
