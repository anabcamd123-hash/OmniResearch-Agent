import json
from datetime import datetime
from backend.runtime.redis_client import redis_client


class WorkflowState:

    PREFIX = "workflow:state:"

    def save(
        self,
        workflow_id: str,
        state: dict,
    ):

        redis_client.set(
            self.PREFIX + workflow_id,
            json.dumps(state),
        )

    def load(self, workflow_id: str):

        data = redis_client.get(
            self.PREFIX + workflow_id
        )

        if not data:
            return None

        return json.loads(data)

    def exists(self, workflow_id: str):

        return redis_client.exists(
            self.PREFIX + workflow_id
        )

    def list_running(self):

        keys = redis_client.keys(
            self.PREFIX + "*"
        )

        running = []

        for key in keys:
            data = redis_client.get(key)
            if data:
                state = json.loads(data)
                if state.get("status") == "running":
                    running.append(state)

        return running

    def delete(self, workflow_id: str):

        redis_client.delete(
            self.PREFIX + workflow_id
        )


workflow_state = WorkflowState()
