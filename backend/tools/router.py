"""
ToolRouter - 路由选择 + 通过 Sandbox 执行

架构:
  Agent → ToolRouter → Sandbox → Tool

所有工具调用必须经过 Sandbox：
  ✓ 超时保护
  ✓ 异常隔离
  ✓ 隔舱隔离
  ✓ 审计日志
  ✓ 熔断器
"""

from backend.tools.registry import registry
from backend.tools.sandbox import sandbox
from backend.tools.result import ToolResult
from backend.tools.circuit_breaker import CircuitBreaker
from backend.runtime.dlq import dlq_push
from backend.llm.provider_factory import get_provider
from backend.utils.logger import logger
from backend.config.settings import settings
from backend.runtime.metrics import metrics


class ToolRouter:

    def __init__(self):

        self.registry = registry
        self._llm = None  # lazy init

        # Circuit Breaker per tool
        self.breakers: dict[str, CircuitBreaker] = {}
        for name in self.registry.tools:
            self.breakers[name] = CircuitBreaker(
                threshold=settings.BREAKER_THRESHOLD,
                recovery_time=settings.BREAKER_RECOVERY_TIME,
            )

    async def select_tool(
        self,
        task: str,
        context: str = "",
    ) -> str:
        """LLM 选择工具"""
        tool_desc = self.registry.list_tools()

        tools_text = "\n".join([
            f"- {name}: {desc}"
            for name, desc in tool_desc.items()
        ])

        context_text = ""
        if context:
            context_text = (
                "Context from past experiences:\n"
                + context
            )

        prompt = (
            f"You are a tool selection system.\n\n"
            f"Task:\n{task}\n\n"
            f"{context_text}\n\n"
            f"Available tools:\n{tools_text}\n\n"
            f"Return ONLY the tool name "
            f"(github/pdf/web/rag)."
        )

        if self._llm is None:
            self._llm = get_provider()
        tool_name = self._llm.invoke(prompt)
        tool_name = tool_name.strip().lower()

        if tool_name not in self.registry.tools:
            tool_name = "web"

        return tool_name

    async def execute(
        self,
        task: str,
        tool_name: str = None,
    ) -> ToolResult:
        """
        执行工具

        所有工具调用必须经过此方法：
        1. 选择工具
        2. Circuit Breaker 检查
        3. Sandbox.execute（含超时+隔舱+审计）
        4. 失败入 DLQ

        禁止直接调用 tool.run()
        """

        # ── 工具选择 ──────────────────────
        if not tool_name:
            rag_tool = self.registry.get("rag")
            past_context = ""
            try:
                rag_result = await sandbox.execute(
                    "rag",
                    rag_tool.run,
                    task,
                )
                if rag_result.success:
                    past_context = str(
                        rag_result.content
                    )
            except Exception:
                pass

            tool_name = await self.select_tool(
                task, past_context
            )

        tool = self.registry.get(tool_name)
        if not tool:
            tool = self.registry.get("rag")
            tool_name = "rag"

        # ── Circuit Breaker 检查 ──────────
        breaker = self.breakers.get(tool_name)
        if breaker and not breaker.allow():
            logger.warning(
                f"[ToolRouter] Circuit OPEN: "
                f"{tool_name}"
            )
            return ToolResult(
                success=False,
                error=(
                    f"Tool '{tool_name}' unavailable "
                    f"(circuit breaker open)"
                ),
                metadata={"tool_name": tool_name},
            )

        # ── 通过 Sandbox 执行 ─────────────
        metrics.tool_calls += 1
        metrics.tool_usage[tool_name] += 1
        logger.info(
            f"[ToolRouter] Executing: {tool_name}"
        )

        result = await sandbox.execute(
            tool_name,
            tool.run,
            task,
        )

        # ── 更新 Circuit Breaker ──────────
        if result.success:
            if breaker:
                breaker.success()
        else:
            if breaker:
                breaker.fail()
            # DLQ
            await dlq_push(
                f"tool_{tool_name}_{id(task)}",
                tool_name,
                result.error or "unknown",
            )

        return result

    def get_breaker_status(self) -> dict:
        """返回所有工具的熔断器状态"""
        return {
            name: breaker.status
            for name, breaker in self.breakers.items()
        }


tool_router = ToolRouter()
