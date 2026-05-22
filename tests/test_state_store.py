"""
Test: StateStore 自动降级
"""

import pytest
from backend.storage.mem_state import (
    MemStateRepository,
)
from backend.storage.sqlite_state import (
    SQLiteStateRepository,
)


@pytest.mark.asyncio
async def test_mem_store():
    store = MemStateRepository()
    await store.set("key1", "value1")
    assert await store.get("key1") == "value1"
    await store.delete("key1")
    assert await store.get("key1") is None


@pytest.mark.asyncio
async def test_sqlite_store(tmp_path):
    db = str(tmp_path / "test.db")
    store = SQLiteStateRepository(db)
    await store.set("key1", "value1")
    assert await store.get("key1") == "value1"
    await store.delete("key1")
    assert await store.get("key1") is None


@pytest.mark.asyncio
async def test_build_state_repo():
    from backend.storage.state_factory import (
        build_state_repo,
    )
    repo = await build_state_repo()
    assert repo is not None
    await repo.set("test", "ok")
    assert await repo.get("test") == "ok"
