import time
import asyncio
from backend.executor.task_graph import TaskGraph
from backend.executor.auto_fix_executor import AutoFixExecutor
from backend.agents.research_agent import ResearchAgent
from backend.agents.reflection_agent import ReflectionAgent
from backend.utils.logger import stream_log
from backend.runtime.runtime_state import state

MAX_RETRIES = 2


class DAGExecutor:
    def __init__(self):
        self.completed_tasks = set()
        self.auto_fix = AutoFixExecutor()
        self.researcher = ResearchAgent()
        self.reflector = ReflectionAgent()

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
        retries = 0
        while retries <= MAX_RETRIES:
            task.status = "running"
            task.start_time = time.time()
            await stream_log(
                f"[Executor] Running task: "
                f"{task.task_id}"
            )

            state.timeline.append({
                "agent": task.task_type.capitalize(),
                "event": "started",
            })

            try:
                result = None

                if task.task_type == "coding":
                    result = await self.auto_fix.run(
                        task.task_id
                    )

                elif task.task_type == "research":
                    result = self.researcher.run(
                        task.task_id
                    )

                elif task.task_type == "reflection":
                    result = self.reflector.run(
                        {"score": 0.9}
                    )

                else:
                    await asyncio.sleep(1)
                    result = {"status": "done"}

                task.end_time = time.time()
                task.duration = (
                    task.end_time - task.start_time
                )
                task.status = "completed"
                self.completed_tasks.add(task.task_id)
                await stream_log(
                    f"[Executor] Completed: "
                    f"{task.task_id}"
                )

                state.timeline.append({
                    "agent": task.task_type.capitalize(),
                    "event": "completed",
                })

                break

            except Exception as e:
                task.end_time = time.time()
                task.duration = (
                    task.end_time - task.start_time
                )
                retries += 1
                task.status = "pending"
                await stream_log(
                    f"[Executor] Failed: "
                    f"{task.task_id} retry {retries}: "
                    f"{e}"
                )

                state.timeline.append({
                    "agent": task.task_type.capitalize(),
                    "event": "failed",
                })
