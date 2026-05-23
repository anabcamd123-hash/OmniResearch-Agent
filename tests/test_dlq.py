"""
Test: DLQ 队列
"""

import pytest
import pytest_asyncio
from backend.runtime.dlq import (
    dlq_push,
    dlq_list,
    dlq_pop,
    dlq_remove,
    dlq_count,
)


@pytest_asyncio.fixture(autouse=True)
async def cleanup_dlq():
    """每个测试前后清理 DLQ"""
    tasks = await dlq_list(limit=1000)
    for t in tasks:
        await dlq_remove(t["task_id"])
    yield
    tasks = await dlq_list(limit=1000)
    for t in tasks:
        await dlq_remove(t["task_id"])


@pytest.mark.asyncio
async def test_dlq_add_and_list():
    await dlq_push("task_1", "research", "test error")
    count = await dlq_count()
    assert count >= 1
    tasks = await dlq_list(limit=10)
    assert any(t["task_id"] == "task_1" for t in tasks)


@pytest.mark.asyncio
async def test_dlq_pop():
    await dlq_push("task_pop", "coding", "boom")
    task = await dlq_pop()
    assert task is not None
    assert task["task_id"] == "task_pop"


@pytest.mark.asyncio
async def test_dlq_remove():
    await dlq_push("task_del", "verify", "to delete")
    await dlq_remove("task_del")
    tasks = await dlq_list(limit=10)
    assert not any(t["task_id"] == "task_del" for t in tasks)
