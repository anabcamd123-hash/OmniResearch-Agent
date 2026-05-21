from backend.storage.repository import MemoryRepository


class MemoryStore:

    def __init__(self):

        self.repo = MemoryRepository()

    async def add(
        self,
        item,
        source="agent"
    ):

        await self.repo.add_memory(
            content=str(item),
            source=source
        )

    async def get_recent(
        self,
        limit=10
    ):

        rows = await self.repo.get_recent(limit)

        return [
            r["content"]
            for r in rows
        ]

    async def clear(self):

        await self.repo.clear()


memory = MemoryStore()
