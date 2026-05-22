"""
ReflectionAgent - 反射 Agent（JSON 输出）

旧版: "true" in output.lower() → 危险
新版: json.loads(response) → 结构化
"""

import json
import asyncio
from backend.agents.base_agent import BaseAgent
from backend.agents.reflection_result import (
    ReflectionResult,
)
from backend.agents.result import AgentResult
from backend.executor.context import ExecutionContext
from backend.utils.logger import logger, log_tokens
from backend.runtime.event_bus import event_bus
from backend.runtime.event_types import (
    AGENT_STARTED,
    AGENT_COMPLETED,
)
from backend.storage.repository import MemoryRepository
from backend.llm.provider_factory import get_provider

llm = get_provider()


class ReflectionAgent(BaseAgent):

    def __init__(self):
        self.llm = get_provider()
        self.memory_repo = MemoryRepository()

    async def run(
        self,
        task: str,
        context: ExecutionContext,
    ) -> ReflectionResult:

        await event_bus.publish(
            AGENT_STARTED,
            {"agent": "reflection"},
        )

        logger.info(
            "[ReflectionAgent] Evaluating..."
        )

        research = context.get("research", "")
        coding = context.get("coding", "")
        verify = context.get("verify", "")
        score = context.get("verify_score", 0)

        prompt = f"""
You are a reflection system.

Task: {task}

Research: {research[:200]}
Code: {coding[:200]}
Verification: {verify[:200]}
Score: {score}/100

Analyze the result quality.

Return ONLY valid JSON.

Schema:
{{
  "need_retry": false,
  "root_cause": "",
  "suggestion": ""
}}

Rules:
- need_retry: true if quality is insufficient
- root_cause: one phrase (e.g. "missing_error_handling")
- suggestion: one sentence fix recommendation
"""

        output = await asyncio.to_thread(
            self.llm.invoke, prompt
        )

        log_tokens(50)

        # 解析 JSON
        try:
            text = output.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])

            data = json.loads(text)

            reflection = ReflectionResult(
                need_retry=data.get(
                    "need_retry", True
                ),
                root_cause=data.get(
                    "root_cause", ""
                ),
                suggestion=data.get(
                    "suggestion", ""
                ),
            )
        except (
            json.JSONDecodeError,
            KeyError,
        ):
            # 解析失败默认需要重试
            reflection = ReflectionResult(
                need_retry=True,
                root_cause="reflection_parse_error",
                suggestion=output.strip(),
            )

        await self.save_learning(
            task, reflection
        )

        # 存入 context
        context.set(
            "reflection_result", reflection
        )

        logger.info(
            f"[ReflectionAgent] "
            f"retry={reflection.need_retry} "
            f"cause={reflection.root_cause}"
        )

        # 兼容旧接口
        agent_result = AgentResult(
            success=not reflection.need_retry,
            content=reflection.suggestion,
            metadata={
                "need_retry": (
                    reflection.need_retry
                ),
                "root_cause": (
                    reflection.root_cause
                ),
            },
        )
        context.set(
            "reflection", reflection.suggestion
        )

        await event_bus.publish(
            AGENT_COMPLETED,
            {"agent": "reflection"},
        )

        return reflection

    async def save_learning(
        self,
        task: str,
        reflection: ReflectionResult,
    ):
        memory_type = (
            "success"
            if not reflection.need_retry
            else "failure"
        )

        summary = (
            f"Task: {task[:80]} | "
            f"Cause: {reflection.root_cause} | "
            f"Fix: {reflection.suggestion}"
        )

        await self.memory_repo.add_memory(
            content=summary,
            source="reflection",
            memory_type=memory_type,
        )
