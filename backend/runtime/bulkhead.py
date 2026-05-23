"""
Bulkhead — 并发隔离（context manager + run 模式）

用法 1 (context manager):
    async with bulkhead.limit("research"):
        await agent.run(task)

用法 2 (实例化):
    bh = Bulkhead(concurrency=2)
    result = await bh.run(coro)
"""

import asyncio
from contextlib import asynccontextmanager

from backend.config.settings import settings


class Bulkhead:

    def __init__(self, concurrency: int = None):
        if concurrency is not None:
            # 简单模式：指定并发数
            self.sem = asyncio.Semaphore(concurrency)
            self.semaphores = None
        else:
            # 任务类型模式
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
            self.sem = None

    async def run(self, coro):
        """执行协程，受并发限制"""
        if self.sem:
            async with self.sem:
                return await coro
        return await coro

    @asynccontextmanager
    async def limit(self, task_type: str):
        """按任务类型限制并发"""
        if self.semaphores:
            sem = self.semaphores.get(
                task_type, self.default_sem
            )
        else:
            sem = self.sem
        async with sem:
            yield


bulkhead = Bulkhead()
