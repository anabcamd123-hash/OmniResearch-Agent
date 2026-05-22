"""
DLQ — 死信队列（aiosqlite 直接操作）

轻量，不走 SQLAlchemy
"""

import aiosqlite
import time

from backend.config.settings import settings

DB_PATH = "data/dlq.db"


async def _get_db():
    db = await aiosqlite.connect(DB_PATH)
    await db.execute(
        """CREATE TABLE IF NOT EXISTS dlq (
            task_id TEXT PRIMARY KEY,
            task_type TEXT,
            error TEXT,
            retries INTEGER DEFAULT 0,
            timestamp REAL
        )"""
    )
    return db


async def dlq_push(task_id: str, task_type: str, error: str):
    """失败任务入 DLQ"""
    db = await _get_db()
    try:
        await db.execute(
            "INSERT OR REPLACE INTO dlq "
            "(task_id, task_type, error, retries, timestamp) "
            "VALUES (?, ?, ?, 0, ?)",
            (task_id, task_type, error, time.time()),
        )
        await db.commit()
    finally:
        await db.close()


async def dlq_list(limit: int = 50) -> list[dict]:
    """列出 DLQ 任务"""
    db = await _get_db()
    try:
        async with db.execute(
            "SELECT task_id, task_type, error, retries, timestamp "
            "FROM dlq ORDER BY timestamp DESC LIMIT ?",
            (limit,),
        ) as cursor:
            rows = await cursor.fetchall()
            return [
                {
                    "task_id": r[0],
                    "task_type": r[1],
                    "error": r[2],
                    "retries": r[3],
                    "timestamp": r[4],
                }
                for r in rows
            ]
    finally:
        await db.close()


async def dlq_pop() -> dict | None:
    """取出最旧任务"""
    db = await _get_db()
    try:
        async with db.execute(
            "SELECT task_id, task_type, error, retries "
            "FROM dlq ORDER BY timestamp ASC LIMIT 1"
        ) as cursor:
            row = await cursor.fetchone()
            if row:
                await db.execute(
                    "DELETE FROM dlq WHERE task_id=?",
                    (row[0],),
                )
                await db.commit()
                return {
                    "task_id": row[0],
                    "task_type": row[1],
                    "error": row[2],
                    "retries": row[3],
                }
            return None
    finally:
        await db.close()


async def dlq_count() -> int:
    """DLQ 条目数"""
    db = await _get_db()
    try:
        async with db.execute(
            "SELECT COUNT(*) FROM dlq"
        ) as cursor:
            row = await cursor.fetchone()
            return row[0] if row else 0
    finally:
        await db.close()


async def dlq_remove(task_id: str):
    """删除指定任务"""
    db = await _get_db()
    try:
        await db.execute(
            "DELETE FROM dlq WHERE task_id=?",
            (task_id,),
        )
        await db.commit()
    finally:
        await db.close()


async def dlq_retry_all():
    """重置所有任务重试计数"""
    db = await _get_db()
    try:
        await db.execute(
            "UPDATE dlq SET retries=0"
        )
        await db.commit()
    finally:
        await db.close()
