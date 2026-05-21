class RuntimeState:

    def __init__(self):

        # Real-time UI state only
        # Persistent data → SQLite
        self.current_dag = ""

        self.timeline = []

        self.agent_status = {
            "planner": "idle",
            "research": "idle",
            "coding": "idle",
            "verify": "idle",
            "reflection": "idle",
        }

state = RuntimeState()
