"""
StateStore 工厂 — 自动降级

Redis → SQLite → Memory
"""

import logging

from backend.storage.mem_state import (
    MemStateRepository,
)
from backend.storage.sqlite_state import (
    SQLiteStateRepository,
)

logger = logging.getLogger(__name__)


async def build_state_repo():
    """
    尝试 Redis → SQLite → Memory
    返回第一个可用的 StateRepository
    """

    # 尝试 Redis
    try:
        from backend.storage.redis_state import (
            RedisStateRepository,
        )
        repo = RedisStateRepository()
        await repo.set("__health__", "1")
        val = await repo.get("__health__")
        if val == "1":
            logger.info(
                "[StateStore] Using Redis"
            )
            return repo
    except Exception as e:
        logger.debug(
            f"[StateStore] Redis unavailable: {e}"
        )

    # 尝试 SQLite
    try:
        repo = SQLiteStateRepository()
        await repo.set("__health__", "1")
        val = await repo.get("__health__")
        if val == "1":
            logger.info(
                "[StateStore] Using SQLite"
            )
            return repo
    except Exception as e:
        logger.debug(
            f"[StateStore] SQLite unavailable: {e}"
        )

    # 降级到 Memory
    logger.info(
        "[StateStore] Using Memory (fallback)"
    )
    return MemStateRepository()
