"""
Layer 6: Retry Policy
指数退避重试，与Circuit Breaker协作
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def retry_async(
    func,
    retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 30.0,
    backoff_factor: float = 2.0,
):
    """
    带指数退避的异步重试

    Args:
        func: 无参协程函数（lambda: tool.execute(query)）
        retries: 最大重试次数（不含首次）
        base_delay: 首次重试延迟（秒）
        max_delay: 最大延迟上限
        backoff_factor: 退避倍数

    Returns:
        执行结果

    Raises:
        最后一次异常

    注意:
        整个 retry 周期对外只算一次失败（对接 Circuit Breaker）
    """
    last_error = None
    delay = base_delay

    for attempt in range(1 + retries):
        try:
            return await func()
        except Exception as e:
            last_error = e
            if attempt < retries:
                logger.warning(
                    f"Retry {attempt + 1}/{retries} "
                    f"after {delay:.1f}s: {e}"
                )
                await asyncio.sleep(delay)
                delay = min(
                    delay * backoff_factor,
                    max_delay,
                )

    raise last_error
