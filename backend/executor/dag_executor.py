import asyncio
from backend.executor.task_graph import TaskGraph
from backend.utils.logger import stream_log

MAX_RETRIES = 2

class DAGExecutor:
    def __init__(self):
        self.completed_tasks = set()

    async def execute(self, tasks):
        graph = TaskGraph()
        for task in tasks:
            graph.add_task(task)

        while len(self.completed_tasks) < len(tasks):
            ready_tasks = graph.get_ready_tasks(self.completed_tasks)
            if not ready_tasks:
                break
            await asyncio.gather(*[self.run_task(task) for task in ready_tasks])

    async def run_task(self, task):
        retries = 0
        while retries <= MAX_RETRIES:
            task.status = 'running'
            await stream_log(f'[Executor] Running task: {task.task_id}')
            try:
                # 模拟任务执行
                await asyncio.sleep(1)
                if task.task_id == 'verify' and retries < 1:
                    raise Exception('Simulated failure')
                task.status = 'completed'
                self.completed_tasks.add(task.task_id)
                await stream_log(f'[Executor] Completed task: {task.task_id}')
                break
            except Exception as e:
                retries += 1
                task.status = 'pending'
                await stream_log(f'[Executor] Task {task.task_id} failed, retry {retries}: {e}')
