"""
Test: DAGScheduler 调度逻辑
"""

import pytest
from backend.executor.dag_scheduler import (
    DAGScheduler,
)
from backend.executor.task_queue import TaskQueue
from backend.executor.task import Task


@pytest.mark.asyncio
async def test_scheduler_basic():
    queue = TaskQueue()

    tasks = [
        Task(
            task_id="a",
            task_type="research",
            dependencies=[],
        ),
        Task(
            task_id="b",
            task_type="coding",
            dependencies=["a"],
        ),
    ]

    scheduler = DAGScheduler(tasks, queue)

    import asyncio

    async def run_scheduler():
        await scheduler.schedule_loop()

    async def consume():
        collected = []
        for _ in range(2):
            t = await queue.dequeue()
            collected.append(t.id)
            scheduler.mark_done(t.id)
        return collected

    sched_task = asyncio.create_task(
        run_scheduler()
    )
    result = await consume()
    sched_task.cancel()

    assert "a" in result
    assert "b" in result
    assert result.index("a") < result.index("b")


@pytest.mark.asyncio
async def test_scheduler_parallel():
    queue = TaskQueue()

    tasks = [
        Task(
            task_id="a1",
            task_type="research",
            dependencies=[],
        ),
        Task(
            task_id="a2",
            task_type="research",
            dependencies=[],
        ),
        Task(
            task_id="b",
            task_type="coding",
            dependencies=["a1", "a2"],
        ),
    ]

    scheduler = DAGScheduler(tasks, queue)

    import asyncio

    async def run_scheduler():
        await scheduler.schedule_loop()

    async def consume():
        collected = []
        for _ in range(3):
            t = await queue.dequeue()
            collected.append(t.id)
            scheduler.mark_done(t.id)
        return collected

    sched_task = asyncio.create_task(
        run_scheduler()
    )
    result = await consume()
    sched_task.cancel()

    # a1, a2 should come before b
    b_idx = result.index("b")
    assert result.index("a1") < b_idx
    assert result.index("a2") < b_idx
