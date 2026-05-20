from backend.utils.logger import stream_log

from backend.agents.research_agent import ResearchAgent
from backend.agents.coding_agent import CodingAgent
from backend.agents.verify_agent import VerifyAgent
from backend.agents.reflection_agent import ReflectionAgent


class DAGExecutor:

    def __init__(self):

        self.agents = {
            "research": ResearchAgent(),
            "coding": CodingAgent(),
            "verify": VerifyAgent(),
            "reflection": ReflectionAgent(),
        }

    async def execute(self, tasks):

        completed = set()
        results = {}

        while len(completed) < len(tasks):

            for task in tasks:

                if task.task_id in completed:
                    continue

                if not task.is_ready(completed):
                    continue

                await stream_log(
                    f"[Executor] Running task: {task.task_id}"
                )

                agent = self.agents[task.task_type]

                prev_result = None
                if task.dependencies:
                    prev_key = task.dependencies[-1]
                    prev_result = results.get(prev_key)

                if task.task_type == "research":
                    result = agent.run("transformer papers")
                elif task.task_type == "coding":
                    result = agent.run(prev_result)
                elif task.task_type == "verify":
                    result = agent.run(prev_result)
                elif task.task_type == "reflection":
                    result = agent.run(prev_result)
                else:
                    result = {}

                results[task.task_id] = result
                task.status = "completed"
                completed.add(task.task_id)

                await stream_log(
                    f"[Executor] Completed task: {task.task_id}"
                )
                MAX_RETRIES = 2

async def run_task(self, task):
    retries = 0
    while retries <= MAX_RETRIES:
        task.status = "running"
        await stream_log(f"[Executor] Running task: {task.task_id}")
        try:
            # 模拟执行
            await asyncio.sleep(1)
            # 假设 verify task 模拟失败
            if task.task_id == "verify" and retries < 1:
                raise Exception("Simulated failure")
            task.status = "completed"
            self.completed_tasks.add(task.task_id)
            await stream_log(f"[Executor] Completed task: {task.task_id}")
            break
        except Exception as e:
            retries += 1
            await stream_log(f"[Executor] Task {task.task_id} failed, retry {retries}: {e}")
            task.status = "pending"
