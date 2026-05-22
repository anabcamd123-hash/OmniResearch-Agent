"""
TaskGraph — 任务依赖图
"""

from backend.executor.task import Task


class TaskGraph:

    def __init__(self):
        self.tasks: list[Task] = []

    def add_task(self, task: Task):
        self.tasks.append(task)

    def get_ready_tasks(
        self, completed: set
    ) -> list[Task]:
        return [
            t
            for t in self.tasks
            if t.status == "pending"
            and t.is_ready(completed)
        ]

    def total(self) -> int:
        return len(self.tasks)
