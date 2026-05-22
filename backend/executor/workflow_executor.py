"""
WorkflowExecutor — 唯一入口

Planner → DAG → Agent 链式执行（传递上下文）
自修复循环：Coding → Verify → Reflection → (retry Coding)
"""

import uuid
import asyncio

from backend.agents.planner_agent import PlannerAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.coding_agent import CodingAgent
from backend.agents.verify_agent import VerifyAgent
from backend.agents.reflection_agent import (
    ReflectionAgent,
)
from backend.runtime.runtime_state import state
from backend.storage.repository import (
    TaskRepository,
    WorkflowRepository,
    MemoryRepository,
)
from backend.utils.logger import logger

MAX_FIX_LOOP = 3


class WorkflowExecutor:

    def __init__(self):
        self.planner = PlannerAgent()
        self.researcher = ResearchAgent()
        self.coder = CodingAgent()
        self.verifier = VerifyAgent()
        self.reflector = ReflectionAgent()
        self.task_repo = TaskRepository()
        self.workflow_repo = WorkflowRepository()
        self.memory_repo = MemoryRepository()

    async def execute(self, task: str):
        workflow_id = str(uuid.uuid4())[:8]
        logger.info(
            f"[Workflow] Starting {workflow_id}"
        )

        # 创建 workflow
        await self.workflow_repo.create_workflow(
            workflow_id=workflow_id,
            objective=task,
            total_tasks=4,
        )
        await self.workflow_repo.update_status(
            workflow_id, "running"
        )

        # ── Phase 1: Research ─────────────
        await self._record_task(
            workflow_id, "research", "running"
        )
        research_result = await self.researcher.run(
            task
        )
        await self._record_task(
            workflow_id, "research", "completed"
        )

        # ── Phase 2-4: Coding → Verify → 反馈循环 ──
        coding_result = None
        verify_result = None

        for attempt in range(MAX_FIX_LOOP + 1):
            # Coding
            await self._record_task(
                workflow_id, "coding", "running"
            )
            coding_result = await self.coder.run(
                research_result
            )
            await self._record_task(
                workflow_id, "coding",
                "completed"
                if coding_result.success
                else "failed",
            )

            # Verify
            await self._record_task(
                workflow_id, "verify", "running"
            )
            verify_result = await self.verifier.run(
                coding_result
            )
            await self._record_task(
                workflow_id, "verify",
                "completed"
                if verify_result.passed
                else "failed",
            )

            if verify_result.passed:
                break

            # Reflection
            await self._record_task(
                workflow_id,
                "reflection",
                "running",
            )
            reflection = await self.reflector.run(
                task, verify_result
            )
            await self._record_task(
                workflow_id, "reflection",
                "completed",
            )

            if not reflection.need_retry:
                break

            if attempt < MAX_FIX_LOOP:
                logger.info(
                    f"[Workflow] AutoFix "
                    f"attempt {attempt + 1}"
                )
                state.auto_fix_stats[
                    "total_retry"
                ] += 1

        # 统计
        completed = 4  # 简化：固定 4 个 phase
        if (
            verify_result
            and verify_result.passed
        ):
            state.auto_fix_stats["success"] += 1
        else:
            state.auto_fix_stats["failed"] += 1

        # 完成
        await self.workflow_repo.complete_workflow(
            workflow_id=workflow_id,
            completed_tasks=completed,
            token_usage=0,
        )

        # 保存学习模式
        try:
            pattern = "research, coding, verify, reflection"
            await self.memory_repo.add_memory(
                content=(
                    f"Task: {task[:80]} | "
                    f"Pattern: {pattern}"
                ),
                source="workflow",
                memory_type="success",
            )
        except Exception:
            pass

        logger.info(
            f"[Workflow] {workflow_id} completed"
        )

        return {
            "workflow_id": workflow_id,
            "status": "completed",
            "research": research_result,
            "coding": coding_result.to_dict()
            if coding_result
            else None,
            "verify": verify_result.to_dict()
            if verify_result
            else None,
        }

    async def _record_task(
        self,
        workflow_id: str,
        task_id: str,
        status: str,
    ):
        """记录 task 状态"""
        task_key = f"{workflow_id}_{task_id}"
        try:
            await self.task_repo.update_status(
                task_key, status
            )
        except Exception:
            pass
