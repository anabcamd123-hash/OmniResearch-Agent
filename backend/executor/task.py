from typing import List
import time

class Task:

    def __init__(
        self,
        task_id: str,
        task_type: str,
        dependencies: List[str] = None
    ):

        self.task_id = task_id

        self.task_type = task_type

        self.dependencies = dependencies or []

        self.status = "pending"

        self.start_time = None

        self.end_time = None

    def is_ready(self, completed_tasks):

        return all(
            dep in completed_tasks
            for dep in self.dependencies
        )
