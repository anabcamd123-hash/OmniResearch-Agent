import uuid
from backend.agents.planner_agent import PlannerAgent
from backend.executor.dag_executor import DAGExecutor
from backend.utils.logger import stream_log
from backend.runtime.runtime_state import state
from backend.storage.repository import (
    TaskRepository,
    WorkflowRepository,
)


class WorkflowExecutor:

    def __init__(self):

        self.planner = PlannerAgent()

        self.dag_executor = DAGExecutor()

        self.task_repo = TaskRepository()

        self.workflow_repo = WorkflowRepository()

    async def execute(self, task: str):

        workflow_id = str(uuid.uuid4())[:8]

        await stream_log(
            f"[System] Starting DAG workflow "
            f"{workflow_id}"
        )

        # Create workflow in DB
        await self.workflow_repo.create_workflow(
            workflow_id=workflow_id,
            objective=task,
            total_tasks=4,
        )

        await self.workflow_repo.update_status(
            workflow_id, "running"
        )

        # Create plan
        tasks = await self.planner.create_plan(task)

        state.total_tasks += len(tasks)
        state.running_tasks = len(tasks)

        # Create tasks in DB
        for t in tasks:
            await self.task_repo.create_task(
                task_id=f"{workflow_id}_{t.task_id}",
                objective=t.task_id,
            )

        # Execute
        for t in tasks:
            await self.task_repo.update_status(
                f"{workflow_id}_{t.task_id}",
                "running",
            )

        await self.dag_executor.execute(tasks)

        # Mark completed
        for t in tasks:
            await self.task_repo.save_result(
                f"{workflow_id}_{t.task_id}",
                str(t.status),
                duration=0,
            )
            await self.task_repo.update_status(
                f"{workflow_id}_{t.task_id}",
                "completed" if t.status == "completed" else "failed",
            )

        state.completed_tasks += len(tasks)
        state.running_tasks = 0

        await self.workflow_repo.complete_workflow(
            workflow_id=workflow_id,
            completed_tasks=len(tasks),
            token_usage=state.token_usage,
        )

        await stream_log(
            f"[System] Workflow {workflow_id} completed"
        )

        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "tasks": [
                {
                    "task_id": t.task_id,
                    "status": t.status
                }
                for t in tasks
            ]
        }
