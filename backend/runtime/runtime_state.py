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

        # 每个任务的状态（前端交互用）
        # key: task_id
        # value: {status, output, retries, agent, duration}
        self.task_status: dict = {}

    def update_task(
        self,
        task_id: str,
        status: str,
        output: str = "",
        retries: int = 0,
        agent: str = "",
        duration: float = 0,
    ):
        self.task_status[task_id] = {
            "status": status,
            "output": output,
            "retries": retries,
            "agent": agent,
            "duration": round(duration, 2),
        }


state = RuntimeState()
