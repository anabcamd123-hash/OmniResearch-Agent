"""
Bulkhead — 并发隔离（context manager 模式）

用法:
    async with bulkhead.limit("research"):
        await agent.run(task)
"""

import asyncio
from contextlib import asynccontextmanager

from backend.config.settings import settings


class Bulkhead:

    def __init__(self):
        self.semaphores = {
            "github": asyncio.Semaphore(
                settings.TOOL_LIMIT_GITHUB
            ),
            "pdf": asyncio.Semaphore(
                settings.TOOL_LIMIT_PDF
            ),
            "rag": asyncio.Semaphore(
                settings.TOOL_LIMIT_RAG
            ),
            "research": asyncio.Semaphore(
                settings.BULKHEAD_RESEARCH
            ),
            "coding": asyncio.Semaphore(
                settings.BULKHEAD_CODING
            ),
            "verify": asyncio.Semaphore(
                settings.BULKHEAD_VERIFY
            ),
            "reflection": asyncio.Semaphore(
                settings.BULKHEAD_REFLECTION
            ),
        }
        self.default_sem = asyncio.Semaphore(3)

    @asynccontextmanager
    async def limit(self, task_type: str):
        sem = self.semaphores.get(
            task_type, self.default_sem
        )
        async with sem:
            yield


bulkhead = Bulkhead()
