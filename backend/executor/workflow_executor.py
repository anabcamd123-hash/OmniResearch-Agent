from backend.agents.planner_agent import PlannerAgent

from backend.executor.dag_executor import DAGExecutor

from backend.utils.logger import stream_log


class WorkflowExecutor:

    def __init__(self):

        self.planner = PlannerAgent()

        self.dag_executor = DAGExecutor()

    async def execute(self, task: str):

        await stream_log(
            "[System] Starting DAG workflow"
        )

        tasks = await self.planner.create_plan(task)

        await self.dag_executor.execute(tasks)

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
