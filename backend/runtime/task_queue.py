import json
from backend.runtime.redis_client import redis_client


class TaskQueue:

    KEY = "omniresearch:task_queue"

    def push(self, task: dict):

        redis_client.lpush(
            self.KEY,
            json.dumps(task),
        )

    def pop(self):

        data = redis_client.rpop(self.KEY)

        if not data:
            return None

        return json.loads(data)

    def size(self):

        return redis_client.llen(self.KEY)

    def clear(self):

        redis_client.delete(self.KEY)


task_queue = TaskQueue()
