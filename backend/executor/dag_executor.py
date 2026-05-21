import asyncio
import time
from backend.runtime.task_queue import task_queue
from backend.runtime.task_state import task_state
from backend.runtime.workflow_state import workflow_state
from backend.agents.registry import registry
from backend.executor.context import ExecutionContext
from backend.agents.reflection_agent import ReflectionAgent
from backend.runtime.event_bus import event_bus
from backend.runtime.event_types import (
    TASK_STARTED,
    TASK_COMPLETED,
    TASK_FAILED,
    TASK_RETRY,
)
from backend.runtime.agent_stats import agent_stats
from backend.utils.logger import logger


class DAGExecutor:

    def __init__(self):

        self.queue = task_queue

        self.registry = registry

        self.reflector = ReflectionAgent()

        self.context = ExecutionContext()

        self.running = False

    async def execute(
        self,
        tasks,
        workflow_id=None,
    ):

        workflow_id = workflow_id or "unknown"

        # Init workflow state
        initial_state = {
            "workflow_id": workflow_id,
            "status": "running",
            "completed": [],
            "failed": [],
            "pending": [
                t.task_id for t in tasks
            ],
            "created_at": (
                time.strftime("%Y-%m-%d %H:%M:%S")
            ),
        }

        workflow_state.save(
            workflow_id,
            initial_state,
        )

        # Push all tasks to queue
        for t in tasks:

            self.queue.push({
                "workflow_id": workflow_id,
                "task_id": t.task_id,
                "task_type": t.task_type,
                "payload": getattr(
                    t, "payload", None
                ),
                "dependencies": getattr(
                    t, "dependencies", []
                ),
                "retry": 0,
                "max_retry": 2,
            })

            task_state.save(
                t.task_id, "pending"
            )

        # Start worker pool
        await self.run_worker_pool(
            worker_count=3
        )

        # Mark workflow complete
        state = workflow_state.load(workflow_id)

        if state:
            state["status"] = (
                "completed"
                if not state["failed"]
                else "partial"
            )
            workflow_state.save(
                workflow_id, state
            )

    async def run_worker_pool(
        self,
        worker_count=3,
    ):

        self.running = True

        workers = [
            asyncio.create_task(
                self.worker(i)
            )
            for i in range(worker_count)
        ]

        # Monitor: stop when queue empty
        # for 2 seconds
        empty_count = 0

        while self.running:

            if self.queue.size() == 0:
                empty_count += 1
                if empty_count > 4:
                    self.running = False
                    break
            else:
                empty_count = 0

            await asyncio.sleep(0.5)

        for w in workers:
            w.cancel()

    async def worker(self, worker_id: int):

        while self.running:

            task = self.queue.pop()

            if not task:
                await asyncio.sleep(0.5)
                continue

            await self.run_task(task)

    async def run_task(self, task: dict):

        task_id = task["task_id"]
        task_type = task["task_type"]
        workflow_id = task["workflow_id"]

        task_state.save(task_id, "running")

        await event_bus.publish(
            TASK_STARTED,
            {
                "task_id": task_id,
                "task_type": task_type,
                "workflow_id": workflow_id,
            },
        )

        start = time.time()

        agent = self.registry.get(task_type)

        try:

            result = await agent.run(
                task.get("payload", task_id),
                self.context,
            )

            duration = time.time() - start

            task_state.save(
                task_id, "completed"
            )

            # Update workflow state
            state = workflow_state.load(
                workflow_id
            )

            if state:
                if task_id in state["pending"]:
                    state["pending"].remove(
                        task_id
                    )
                state["completed"].append(
                    task_id
                )
                workflow_state.save(
                    workflow_id, state
                )

            agent_stats.record(
                task_type, duration
            )

            await event_bus.publish(
                TASK_COMPLETED,
                {
                    "task_id": task_id,
                    "task_type": task_type,
                    "workflow_id": workflow_id,
                    "duration": duration,
                },
            )

            logger.info(
                f"[Worker] Completed: {task_id} "
                f"({duration:.2f}s)"
            )

        except Exception as e:

            task["retry"] += 1

            if task["retry"] <= task["max_retry"]:

                task_state.save(
                    task_id, "retrying"
                )

                self.queue.push(task)

                await event_bus.publish(
                    TASK_RETRY,
                    {
                        "task_id": task_id,
                        "workflow_id": workflow_id,
                        "retry": task["retry"],
                        "error": str(e),
                    },
                )

                logger.info(
                    f"[Worker] Retry "
                    f"{task['retry']}: {task_id}"
                )

            else:

                task_state.save(
                    task_id, "failed"
                )

                state = workflow_state.load(
                    workflow_id
                )

                if state:
                    if task_id in state["pending"]:
                        state["pending"].remove(
                            task_id
                        )
                    state["failed"].append(
                        task_id
                    )
                    workflow_state.save(
                        workflow_id, state
                    )

                await event_bus.publish(
                    TASK_FAILED,
                    {
                        "task_id": task_id,
                        "workflow_id": workflow_id,
                        "error": str(e),
                    },
                )

                logger.info(
                    f"[Worker] Failed: {task_id}"
                )

    async def resume_workflow(
        self,
        workflow_id: str,
    ):

        state = workflow_state.load(
            workflow_id
        )

        if not state:
            logger.info(
                f"[Resume] No state: "
                f"{workflow_id}"
            )
            return

        pending = state.get("pending", [])

        if not pending:
            logger.info(
                f"[Resume] No pending: "
                f"{workflow_id}"
            )
            return

        logger.info(
            f"[Resume] {workflow_id}: "
            f"{len(pending)} tasks"
        )

        for task_id in pending:

            self.queue.push({
                "workflow_id": workflow_id,
                "task_id": task_id,
                "task_type": (
                    task_id.split("_")[0]
                ),
                "payload": None,
                "retry": 0,
                "max_retry": 2,
            })

        await self.run_worker_pool(
            worker_count=3
        )
