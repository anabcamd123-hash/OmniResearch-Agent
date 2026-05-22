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
            "autofix": "idle",
        }

        # AutoFix 统计
        self.auto_fix_stats = {
            "success": 0,
            "failed": 0,
            "total_retry": 0,
        }


state = RuntimeState()
