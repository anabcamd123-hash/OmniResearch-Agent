"""
Test: retry_async 重试逻辑
"""

import pytest
from backend.executor.retry import retry_async


@pytest.mark.asyncio
async def test_retry_success_first():
    call_count = 0

    async def succeed():
        nonlocal call_count
        call_count += 1
        return "ok"

    result = await retry_async(succeed, retries=3)
    assert result == "ok"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_after_failures():
    call_count = 0

    async def fail_then_succeed():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ValueError("not yet")
        return "ok"

    result = await retry_async(
        fail_then_succeed,
        retries=3,
        delay=0.01,
    )
    assert result == "ok"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_exhausted():
    async def always_fail():
        raise RuntimeError("boom")

    with pytest.raises(RuntimeError):
        await retry_async(
            always_fail,
            retries=2,
            delay=0.01,
        )
