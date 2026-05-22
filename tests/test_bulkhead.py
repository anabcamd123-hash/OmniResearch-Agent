"""
Test: Bulkhead 并发隔离
"""

import asyncio
import pytest
from backend.runtime.bulkhead import Bulkhead


@pytest.mark.asyncio
async def test_bulkhead_limits_concurrency():
    bh = Bulkhead(2)
    active = 0
    max_active = 0

    async def task():
        nonlocal active, max_active
        active += 1
        max_active = max(max_active, active)
        await asyncio.sleep(0.1)
        active -= 1

    await asyncio.gather(
        *[bh.run(task()) for _ in range(5)]
    )
    assert max_active <= 2


@pytest.mark.asyncio
async def test_bulkhead_returns_result():
    bh = Bulkhead(1)

    async def compute():
        return 42

    result = await bh.run(compute())
    assert result == 42
