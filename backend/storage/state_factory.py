"""
StateStore 工厂 — 自动降级

Redis → SQLite → Memory
"""

import logging

from backend.storage.mem_state import MemStateRepository
from backend.storage.sqlite_state import SQLiteStateRepository

logger = logging.getLogger(__name__)


async def build_state_repo():
    """自动选择最佳可用后端"""
    # Redis
    try:
        from backend.storage.redis_state import RedisStateRepository
        repo = RedisStateRepository()
        await repo.set("__health__", "1")
        if await repo.get("__health__") == "1":
            logger.info("[StateStore] Using Redis")
            return repo
    except Exception as e:
        logger.debug(f"[StateStore] Redis: {e}")

    # SQLite
    try:
        repo = SQLiteStateRepository()
        await repo.set("__health__", "1")
        if await repo.get("__health__") == "1":
            logger.info("[StateStore] Using SQLite")
            return repo
    except Exception as e:
        logger.debug(f"[StateStore] SQLite: {e}")

    # Memory
    logger.info("[StateStore] Using Memory (fallback)")
    return MemStateRepository()
