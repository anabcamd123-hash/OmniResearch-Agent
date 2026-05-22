"""
WorkflowExecutor — 唯一入口

Planner → DAG → Agent → 完成
"""

import uuid

from backend.agents.planner_agent import PlannerAgent
from backend.executor.dag_executor import DAGExecutor
from backend.runtime.runtime_state import state
from backend.storage.repository import (
    TaskRepository,
    WorkflowRepository,
    MemoryRepository,
)
from backend.utils.logger import logger


class WorkflowExecutor:

    def __init__(self):
        self.planner = PlannerAgent()
        self.dag_executor = DAGExecutor()
        self.task_repo = TaskRepository()
        self.workflow_repo = WorkflowRepository()
        self.memory_repo = MemoryRepository()

    async def execute(self, task: str):
        workflow_id = str(uuid.uuid4())[:8]
        logger.info(
            f"[Workflow] Starting {workflow_id}"
        )

        # Planner 生成 DAG
        tasks = await self.planner.create_plan(task)

        # 创建 workflow
        await self.workflow_repo.create_workflow(
            workflow_id=workflow_id,
            objective=task,
            total_tasks=len(tasks),
        )
        await self.workflow_repo.update_status(
            workflow_id, "running"
        )

        # 创建 task 记录
        for t in tasks:
            await self.task_repo.create_task(
                f"{workflow_id}_{t.id}", t.type
            )
            await self.task_repo.update_status(
                f"{workflow_id}_{t.id}", "running"
            )

        # 执行 DAG
        await self.dag_executor.execute(tasks)

        # 更新结果
        completed = 0
        for t in tasks:
            task_key = f"{workflow_id}_{t.id}"
            status = t.status
            if status == "completed":
                completed += 1
            await self.task_repo.save_result(
                task_key, str(status)
            )
            await self.task_repo.update_status(
                task_key, status
            )

        # 完成 workflow
        await self.workflow_repo.complete_workflow(
            workflow_id=workflow_id,
            completed_tasks=completed,
            token_usage=0,
        )

        # 保存成功模式
        if completed == len(tasks):
            pattern = ", ".join(t.type for t in tasks)
            await self.memory_repo.add_memory(
                content=f"Task: {task[:80]} | Pattern: {pattern}",
                source="workflow",
                memory_type="success",
            )

        logger.info(
            f"[Workflow] {workflow_id} done: "
            f"{completed}/{len(tasks)}"
        )

        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "completed": completed,
            "total": len(tasks),
            "tasks": [
                {"task_id": t.id, "type": t.type, "status": t.status}
                for t in tasks
            ],
        }
