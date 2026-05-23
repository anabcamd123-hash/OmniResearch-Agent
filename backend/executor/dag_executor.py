"""
DAGExecutor — 任务图执行器

直接 gather 并发，不用 Queue+Worker
集成 Bulkhead + DLQ + CircuitBreaker
"""

import asyncio
import time
from collections import defaultdict

from backend.executor.task_graph import TaskGraph
from backend.runtime.bulkhead import bulkhead
from backend.runtime.dlq import dlq_push
from backend.runtime.runtime_state import state
from backend.agents.registry import get_agent
from backend.config.settings import settings
from backend.utils.logger import logger


# ── CircuitBreaker ───────────────────────

class CircuitBreaker:

    def __init__(
        self,
        threshold: int = 3,
        timeout: int = 60,
    ):
        self.threshold = threshold
        self.timeout = timeout
        self.failures = defaultdict(int)
        self.tripped_until = defaultdict(float)

    def is_tripped(self, agent_type: str) -> bool:
        return time.time() < self.tripped_until.get(
            agent_type, 0
        )

    def record_failure(self, agent_type: str):
        self.failures[agent_type] += 1
        if self.failures[agent_type] >= self.threshold:
            self.tripped_until[agent_type] = (
                time.time() + self.timeout
            )

    def record_success(self, agent_type: str):
        self.failures[agent_type] = 0


circuit_breaker = CircuitBreaker(
    threshold=settings.BREAKER_THRESHOLD,
    timeout=settings.BREAKER_RECOVERY_TIME,
)


# ── DAGExecutor ──────────────────────────

class DAGExecutor:

    def __init__(self):
        self.completed_tasks: set = set()

    async def execute(self, tasks):
        graph = TaskGraph()
        for task in tasks:
            graph.add_task(task)

        self.completed_tasks = set()

        while len(self.completed_tasks) < len(tasks):
            ready = graph.get_ready_tasks(
                self.completed_tasks
            )
            if not ready:
                break
            await asyncio.gather(
                *[self.run_task(t) for t in ready]
            )

    async def run_task(self, task):
        agent_type = task.task_type

        # 熔断检查
        if circuit_breaker.is_tripped(agent_type):
            logger.info(
                f"[DAG] Skipping {task.task_id} "
                f"(circuit breaker)"
            )
            task.status = "skipped"
            await dlq_push(
                task.task_id,
                agent_type,
                "circuit_breaker",
            )
            self.completed_tasks.add(task.task_id)
            state.timeline.append(
                {"agent": agent_type.capitalize(), "event": "skipped"}
            )
            return

        async with bulkhead.limit(agent_type):
            try:
                task.status = "running"
                task.start_time = time.time()
                state.timeline.append(
                    {"agent": agent_type.capitalize(), "event": "started"}
                )
                logger.info(
                    f"[DAG] Running {task.task_id} ({agent_type})"
                )

                agent = get_agent(agent_type)
                result = agent.run(task.task_id)
                if asyncio.iscoroutine(result):
                    result = await result

                task.end_time = time.time()
                task.duration = task.end_time - task.start_time
                task.status = "completed"
                self.completed_tasks.add(task.task_id)
                circuit_breaker.record_success(agent_type)

                state.timeline.append(
                    {"agent": agent_type.capitalize(), "event": "completed"}
                )
                logger.info(
                    f"[DAG] {task.task_id} completed ({task.duration:.2f}s)"
                )

            except Exception as e:
                task.end_time = time.time()
                task.duration = task.end_time - task.start_time if task.start_time else 0
                task.status = "failed"
                self.completed_tasks.add(task.task_id)
                circuit_breaker.record_failure(agent_type)

                await dlq_push(
                    task.task_id,
                    agent_type,
                    str(e),
                )

                state.timeline.append(
                    {"agent": agent_type.capitalize(), "event": "failed"}
                )
                logger.error(
                    f"[DAG] {task.task_id} failed: {e}"
                )
