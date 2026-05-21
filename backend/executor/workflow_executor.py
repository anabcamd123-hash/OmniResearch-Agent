import uuid
from backend.agents.planner_agent import PlannerAgent
from backend.executor.dag_executor import DAGExecutor
from backend.executor.context import ExecutionContext
from backend.runtime.event_bus import event_bus
from backend.runtime.event_types import (
    WORKFLOW_STARTED,
    WORKFLOW_COMPLETED,
)
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

        ctx = ExecutionContext()
        ctx.set("objective", task)

        await event_bus.publish(
            WORKFLOW_STARTED,
            {
                "workflow_id": workflow_id,
                "task": task,
            },
        )

        tasks = await self.planner.run(task, ctx)

        await self.workflow_repo.create_workflow(
            workflow_id=workflow_id,
            objective=task,
            total_tasks=len(tasks),
        )
        await self.workflow_repo.update_status(
            workflow_id, "running"
        )

        for t in tasks:
            await self.task_repo.create_task(
                task_id=(
                    f"{workflow_id}_{t.task_id}"
                ),
                objective=t.payload or t.task_type,
            )
            await self.task_repo.update_status(
                f"{workflow_id}_{t.task_id}",
                "running",
            )

        # Pass workflow_id to dag_executor
        await self.dag_executor.execute(
            tasks,
            workflow_id=workflow_id,
        )

        completed = 0
        for t in tasks:
            is_done = t.status == "completed"
            if is_done:
                completed += 1

            await self.task_repo.save_result(
                f"{workflow_id}_{t.task_id}",
                str(t.status),
                duration=t.duration or 0,
            )
            await self.task_repo.update_status(
                f"{workflow_id}_{t.task_id}",
                "completed"
                if is_done
                else "failed",
            )

        await self.workflow_repo.complete_workflow(
            workflow_id=workflow_id,
            completed_tasks=completed,
            token_usage=0,
        )

        await event_bus.publish(
            WORKFLOW_COMPLETED,
            {
                "workflow_id": workflow_id,
                "completed": completed,
                "total": len(tasks),
            },
        )

        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "tasks": [
                {
                    "task_id": t.task_id,
                    "task_type": t.task_type,
                    "status": t.status,
                }
                for t in tasks
            ],
        }
