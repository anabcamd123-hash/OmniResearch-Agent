"""
retry_async — 异步重试（指数退避）
"""

import asyncio
import logging

logger = logging.getLogger(__name__)


async def retry_async(
    coro_factory,
    retries: int = 3,
    delay: float = 2.0,
    backoff: float = 2.0,
):
    """
    重试协程

    Args:
        coro_factory: 返回协程的函数（每次重试新建）
        retries: 最大重试次数
        delay: 首次延迟
        backoff: 退避倍数
    """
    last_error = None
    current_delay = delay

    for i in range(retries + 1):
        try:
            return await coro_factory()
        except Exception as e:
            last_error = e
            if i < retries:
                logger.warning(
                    f"[Retry] attempt {i + 1}/"
                    f"{retries + 1}: {e}"
                )
                await asyncio.sleep(
                    current_delay
                )
                current_delay *= backoff

    raise last_error
