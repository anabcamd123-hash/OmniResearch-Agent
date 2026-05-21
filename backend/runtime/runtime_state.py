class RuntimeState:

    def __init__(self):

        self.total_tasks = 0

        self.completed_tasks = 0

        self.running_tasks = 0

        self.token_usage = 0

        self.current_dag = ""

        self.timeline = []

        self.agent_status = {
            "planner": "idle",
            "research": "idle",
            "coding": "idle",
            "verify": "idle",
            "reflection": "idle"
        }

state = RuntimeState()
