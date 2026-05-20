class TaskGraph:

    def __init__(self):

        self.tasks = []

    def add_task(self, task):

        self.tasks.append(task)

    def get_ready_tasks(self, completed_tasks):

        return [
            task
            for task in self.tasks
            if task.status == "pending"
            and task.is_ready(completed_tasks)
        ]
