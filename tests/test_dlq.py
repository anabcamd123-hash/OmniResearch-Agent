"""
Test: DLQ 队列
"""

import pytest
from backend.storage.dlq_repository import (
    DLQRepository,
)


@pytest.mark.asyncio
async def test_dlq_add_and_list():
    dlq = DLQRepository()
    await dlq.add_task("task_1", retries=0)
    tasks = await dlq.list_tasks(limit=10)
    assert any(
        t["task_id"] == "task_1" for t in tasks
    )
    await dlq.remove_task("task_1")


@pytest.mark.asyncio
async def test_dlq_pop():
    dlq = DLQRepository()
    await dlq.add_task("task_pop", retries=1)
    task = await dlq.pop_task()
    assert task is not None
    assert task["task_id"] == "task_pop"
