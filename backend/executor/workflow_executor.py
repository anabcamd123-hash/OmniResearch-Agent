"""
WorkflowExecutor — 端到端闭环执行 + 自动重试队列

支持:
- 并发执行多个 workflow (Bulkhead)
- Reflection 指示重试时自动重新入队
- 异常捕获 + 重试计数
- 状态持久化 (SQLite)
- WebSocket 实时推送

流程:
  Planner → Research → Coding → Verify → Reflection
                         ↓              ↓
                    need_retry?    max_retries?
                         ↓              ↓
                    re-queue         mark failed
"""

import uuid
import asyncio
from collections import deque

from backend.runtime.runtime_state import state
from backend.utils.logger import logger
from backend.storage.repository import (
    TaskRepository,
    WorkflowRepository,
    MemoryRepository,
)
from backend.agents.planner_agent import PlannerAgent
from backend.agents.research_agent import ResearchAgent
from backend.agents.coding_agent import CodingAgent
from backend.agents.verify_agent import VerifyAgent
from backend.agents.reflection_agent import (
    ReflectionAgent,
)
from backend.config.settings import settings

MAX_RETRIES = settings.MAX_RETRY


class WorkflowExecutor:

    def __init__(
        self,
        max_concurrent: int = 2,
    ):
        self.planner = PlannerAgent()
        self.research = ResearchAgent()
        self.coding = CodingAgent()
        self.verify = VerifyAgent()
        self.reflection = ReflectionAgent()
        self.task_repo = TaskRepository()
        self.workflow_repo = WorkflowRepository()
        self.memory_repo = MemoryRepository()

        self.queue: deque = deque()
        self.max_concurrent = max_concurrent
        self.running: set = set()

    async def submit(self, task_desc: str) -> str:
        """提交 workflow 到队列"""
        workflow_id = str(uuid.uuid4())[:8]
        self.queue.append(
            {
                "workflow_id": workflow_id,
                "task_desc": task_desc,
                "retries": 0,
            }
        )
        logger.info(
            f"[Queue] Submitted: {workflow_id}"
        )
        return workflow_id

    async def execute(self, task_desc: str):
        """同步执行单个 workflow（直接跑，不走队列）"""
        wf = {
            "workflow_id": str(uuid.uuid4())[:8],
            "task_desc": task_desc,
            "retries": 0,
        }
        return await self._run_workflow(wf)

    async def run_loop(self):
        """主循环：从队列消费 workflow"""
        logger.info(
            "[Executor] Loop started "
            f"(max_concurrent="
            f"{self.max_concurrent})"
        )

        while True:
            while (
                len(self.running)
                < self.max_concurrent
                and self.queue
            ):
                wf = self.queue.popleft()
                wf_id = wf["workflow_id"]
                self.running.add(wf_id)
                asyncio.create_task(
                    self._run_with_cleanup(wf)
                )

            await asyncio.sleep(0.5)

    async def _run_with_cleanup(self, wf: dict):
        """执行 workflow 并清理 running 状态"""
        wf_id = wf["workflow_id"]
        try:
            await self._run_workflow(wf)
        except Exception as e:
            logger.error(
                f"[Executor] {wf_id} unhandled: "
                f"{e}"
            )
        finally:
            self.running.discard(wf_id)

    async def _run_workflow(self, wf: dict):
        """执行单个 workflow（含自动重试）"""
        wf_id = wf["workflow_id"]
        task_desc = wf["task_desc"]
        retries = wf["retries"]

        logger.info(
            f"[Executor] Running {wf_id} "
            f"(retry={retries})"
        )

        # 创建 workflow 记录
        await self.workflow_repo.create_workflow(
            workflow_id=wf_id,
            objective=task_desc,
            total_tasks=4,
        )
        await self.workflow_repo.update_status(
            wf_id, "running"
        )

        try:
            # 1. Planner
            tasks = await self.planner.create_plan(
                task_desc
            )
            await self._record_tasks(wf_id, tasks)

            # 2. Research
            await self._update_task(
                wf_id, "research", "running"
            )
            research_result = (
                await self.research.run(task_desc)
            )
            await self._update_task(
                wf_id, "research", "completed"
            )

            # 3. Coding
            await self._update_task(
                wf_id, "coding", "running"
            )
            coding_result = await self.coding.run(
                research_result
            )
            await self._update_task(
                wf_id, "coding",
                "completed"
                if coding_result.success
                else "failed",
            )

            # 4. Verify
            await self._update_task(
                wf_id, "verify", "running"
            )
            verify_result = await self.verify.run(
                coding_result
            )
            await self._update_task(
                wf_id, "verify",
                "completed"
                if verify_result.passed
                else "failed",
            )

            # 5. Reflection
            await self._update_task(
                wf_id, "reflection", "running"
            )
            reflection = await self.reflector.run(
                task_desc, verify_result
            )
            await self._update_task(
                wf_id, "reflection", "completed"
            )

            # ── 判定结果 ──────────────────
            if reflection.need_retry:
                if retries < MAX_RETRIES:
                    logger.info(
                        f"[Executor] {wf_id} "
                        f"retry needed "
                        f"({retries + 1}/"
                        f"{MAX_RETRIES})"
                    )
                    wf["retries"] += 1
                    self.queue.append(wf)
                    state.auto_fix_stats[
                        "total_retry"
                    ] += 1
                    return {
                        "workflow_id": wf_id,
                        "status": "requeued",
                    }
                else:
                    logger.info(
                        f"[Executor] {wf_id} "
                        f"max retries reached"
                    )
                    state.auto_fix_stats[
                        "failed"
                    ] += 1
                    await self.workflow_repo.update_status(
                        wf_id, "failed"
                    )
                    return {
                        "workflow_id": wf_id,
                        "status": "failed",
                    }

            # 成功
            state.auto_fix_stats["success"] += 1
            await self.workflow_repo.complete_workflow(
                workflow_id=wf_id,
                completed_tasks=4,
                token_usage=0,
            )

            # 保存学习模式
            try:
                await self.memory_repo.add_memory(
                    content=(
                        f"Task: "
                        f"{task_desc[:80]} | "
                        f"Pattern: research, "
                        f"coding, verify, "
                        f"reflection"
                    ),
                    source="workflow",
                    memory_type="success",
                )
            except Exception:
                pass

            logger.info(
                f"[Executor] {wf_id} completed"
            )

            return {
                "workflow_id": wf_id,
                "status": "completed",
                "coding": coding_result.to_dict()
                if coding_result
                else None,
                "verify": verify_result.to_dict()
                if verify_result
                else None,
            }

        except Exception as e:
            logger.error(
                f"[Executor] {wf_id} error: {e}"
            )

            if retries < MAX_RETRIES:
                wf["retries"] += 1
                self.queue.append(wf)
                logger.info(
                    f"[Executor] {wf_id} "
                    f"re-queued "
                    f"(retry={wf['retries']})"
                )
                return {
                    "workflow_id": wf_id,
                    "status": "requeued",
                }
            else:
                await self.workflow_repo.update_status(
                    wf_id, "failed"
                )
                return {
                    "workflow_id": wf_id,
                    "status": "failed",
                    "error": str(e),
                }

    async def _record_tasks(
        self, wf_id: str, tasks
    ):
        """记录所有 task"""
        for t in tasks:
            try:
                await self.task_repo.create_task(
                    f"{wf_id}_{t.task_id}",
                    t.task_type,
                )
                await self.task_repo.update_status(
                    f"{wf_id}_{t.task_id}",
                    "running",
                )
            except Exception:
                pass

    async def _update_task(
        self,
        wf_id: str,
        task_id: str,
        status: str,
    ):
        """更新 task 状态"""
        try:
            await self.task_repo.update_status(
                f"{wf_id}_{task_id}", status
            )
        except Exception:
            pass

    @property
    def ref(self):
        return self.reflection

    @ref.setter
    def ref(self, val):
        self.reflection = val

    # 兼容: 有些地方用 self.reflector
    @property
    def reflector(self):
        return self.reflection
