"""
Sandbox Executor — 工具执行沙箱

所有 Tool 必须经过 Sandbox 执行
"""

import asyncio
import time
import traceback

from backend.tools.result import ToolResult
from backend.tools.tool_audit import tool_audit
from backend.tools.bulkhead import bulkhead
from backend.config.settings import settings
from backend.utils.logger import logger


class ToolSandbox:

    def __init__(self):
        self.timeout = settings.TOOL_TIMEOUT_DEFAULT

    async def execute(
        self,
        tool_name: str,
        func,
        *args,
        **kwargs,
    ) -> ToolResult:
        """
        执行工具：Bulkhead → Timeout → 审计
        """
        async with bulkhead.limit(tool_name):
            return await (
            self._run(tool_name, func, *args, **kwargs)
        )

    async def _run(
        self, tool_name, func, *args, **kwargs
    ) -> ToolResult:
        start = time.time()
        try:
            content = await asyncio.wait_for(
                func(*args, **kwargs),
                timeout=self.timeout,
            )
            duration = time.time() - start
            tool_audit.add(
                tool=tool_name,
                success=True,
                duration=duration,
            )
            if isinstance(content, ToolResult):
                return content
            return ToolResult(
                success=True, content=content
            )

        except asyncio.TimeoutError:
            duration = time.time() - start
            err = (
                f"{tool_name} timeout "
                f"after {self.timeout}s"
            )
            logger.error(f"[Sandbox] {err}")
            tool_audit.add(
                tool=tool_name,
                success=False,
                duration=duration,
                error=err,
            )
            return ToolResult(
                success=False, error=err
            )

        except Exception:
            duration = time.time() - start
            err = traceback.format_exc()
            logger.error(
                f"[Sandbox] {tool_name}: {err}"
            )
            tool_audit.add(
                tool=tool_name,
                success=False,
                duration=duration,
                error=err,
            )
            return ToolResult(
                success=False, error=err
            )


sandbox = ToolSandbox()
