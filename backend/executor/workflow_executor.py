from backend.agents.planner_agent import PlannerAgent
from backend.executor.dag_executor import DAGExecutor
from backend.utils.logger import stream_log
from backend.runtime.runtime_state import state


class WorkflowExecutor:

    def __init__(self):

        self.planner = PlannerAgent()

        self.dag_executor = DAGExecutor()

    async def execute(self, task: str):

        await stream_log(
            "[System] Starting DAG workflow"
        )

        tasks = await self.planner.create_plan(task)

        state.total_tasks += len(tasks)
        state.running_tasks = len(tasks)

        await self.dag_executor.execute(tasks)

        state.completed_tasks += len(tasks)
        state.running_tasks = 0

        await stream_log(
            "[System] Workflow completed"
        )

        return {
            "status": "completed",
            "tasks": [
                {
                    "task_id": t.task_id,
                    "status": t.status
                }
                for t in tasks
            ]
        }
