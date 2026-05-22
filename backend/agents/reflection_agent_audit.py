"""
ReflectionAgent — 审计 + 学习记忆
"""

from backend.agents.base_agent import BaseAgent
from backend.agents.reflection_result import (
    ReflectionResult,
)
from backend.executor.context import ExecutionContext
from backend.utils.logger import logger
from backend.runtime.runtime_state import state
from backend.llm.provider_factory import get_provider
from backend.storage.repository import MemoryRepository
from backend.storage.repository.audit_repository import (
    audit_repo,
)

llm = get_provider()


class ReflectionAgentAudit(BaseAgent):

    def __init__(self):
        self.memory_repo = MemoryRepository()

    async def run(
        self,
        task: str,
        context: ExecutionContext,
        user: dict = None,
    ) -> ReflectionResult:

        state.agent_status["reflection"] = (
            "running"
        )
        state.timeline.append(
            {
                "agent": "Reflection",
                "event": "started",
            }
        )

        logger.info(
            "[Reflection] Evaluating..."
        )

        if user:
            await audit_repo.add_log(
                user=user.get("sub", "unknown"),
                role=user.get("role", "unknown"),
                action="agent_started",
                target=f"reflection:{task[:50]}",
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

Return ONLY valid JSON:
{{
  "need_retry": false,
  "root_cause": "",
  "suggestion": ""
}}

Rules:
- need_retry: true if quality insufficient
- root_cause: one phrase
- suggestion: one sentence fix
"""

        output = llm.invoke(prompt)

        import json
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
                    "suggestion", "",
                ),
            )
        except Exception:
            reflection = ReflectionResult(
                need_retry=True,
                root_cause="parse_error",
                suggestion=output.strip(),
            )

        # 保存学习
        memory_type = (
            "success"
            if not reflection.need_retry
            else "failure"
        )
        await self.memory_repo.add_memory(
            content=(
                f"Task: {task[:80]} | "
                f"Cause: {reflection.root_cause} | "
                f"Fix: {reflection.suggestion}"
            ),
            source="reflection",
            memory_type=memory_type,
        )

        # 审计
        if user:
            await audit_repo.add_log(
                user=user.get("sub", "unknown"),
                role=user.get("role", "unknown"),
                action="agent_completed",
                target=(
                    f"reflection:"
                    f"retry={reflection.need_retry}"
                    f"|{reflection.root_cause}"
                ),
            )

        state.agent_status["reflection"] = (
            "completed"
        )
        state.timeline.append(
            {
                "agent": "Reflection",
                "event": "completed",
            }
        )

        logger.info(
            f"[Reflection] "
            f"retry={reflection.need_retry} "
            f"cause={reflection.root_cause}"
        )

        return reflection
