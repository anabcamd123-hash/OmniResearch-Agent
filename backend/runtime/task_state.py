from backend.runtime.redis_client import redis_client


class TaskState:

    PREFIX = "task:state:"

    def save(self, task_id: str, state: str):

        redis_client.set(
            self.PREFIX + task_id,
            state,
        )

    def load(self, task_id: str):

        return redis_client.get(
            self.PREFIX + task_id
        )

    def delete(self, task_id: str):

        redis_client.delete(
            self.PREFIX + task_id
        )


task_state = TaskState()
