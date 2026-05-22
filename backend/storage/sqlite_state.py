"""
SQLiteStateRepository — SQLite 状态存储
"""

import aiosqlite

from backend.storage.state_repository import (
    StateRepository,
)

DB_PATH = "runtime.db"


class SQLiteStateRepository(StateRepository):

    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._initialized = False

    async def _ensure_table(self):
        if self._initialized:
            return
        async with aiosqlite.connect(
            self.db_path
        ) as db:
            await db.execute(
                """CREATE TABLE IF NOT EXISTS state (
                    key TEXT PRIMARY KEY,
                    value TEXT
                )"""
            )
            await db.commit()
        self._initialized = True

    async def get(self, key: str):
        await self._ensure_table()
        async with aiosqlite.connect(
            self.db_path
        ) as db:
            async with db.execute(
                "SELECT value FROM state WHERE key=?",
                (key,),
            ) as cursor:
                row = await cursor.fetchone()
                return row[0] if row else None

    async def set(self, key: str, value):
        await self._ensure_table()
        async with aiosqlite.connect(
            self.db_path
        ) as db:
            await db.execute(
                "INSERT OR REPLACE INTO state "
                "(key, value) VALUES (?,?)",
                (key, str(value)),
            )
            await db.commit()

    async def delete(self, key: str):
        await self._ensure_table()
        async with aiosqlite.connect(
            self.db_path
        ) as db:
            await db.execute(
                "DELETE FROM state WHERE key=?",
                (key,),
            )
            await db.commit()
