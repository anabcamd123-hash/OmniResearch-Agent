"""
VerifyAgent - 验证 Agent（JSON 输出）

旧版: re.search(r"score[:\s]*(\d+)", ...) → 脆弱
新版: json.loads(response) → 稳定
"""

import json
import asyncio
from backend.agents.base_agent import BaseAgent
from backend.agents.verify_result import VerifyResult
from backend.agents.result import AgentResult
from backend.executor.context import ExecutionContext
from backend.utils.logger import logger, log_tokens
from backend.runtime.event_bus import event_bus
from backend.runtime.event_types import (
    AGENT_STARTED,
    AGENT_COMPLETED,
)
from backend.llm.provider_factory import get_provider

llm = get_provider()


class VerifyAgent(BaseAgent):

    async def run(
        self,
        task: str,
        context: ExecutionContext,
    ) -> VerifyResult:

        await event_bus.publish(
            AGENT_STARTED,
            {"agent": "verify"},
        )

        logger.info("[VerifyAgent] Evaluating...")

        coding_result = context.get("coding", "")

        prompt = f"""
Evaluate this code result.

Task: {task}

Code:
{coding_result}

Return ONLY valid JSON.

Schema:
{{
  "score": 0,
  "passed": false,
  "issues": [],
  "feedback": ""
}}

Rules:
- score: 0-100
- passed: true if score >= 70
- issues: list of discovered problems
- feedback: one concise paragraph
"""

        response = await asyncio.to_thread(
            llm.invoke, prompt
        )

        log_tokens(50)

        # 解析 JSON
        try:
            # 清理 markdown 代码块
            text = response.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])

            data = json.loads(text)

            verify_result = VerifyResult(
                passed=data.get(
                    "passed", False
                ),
                score=data.get("score", 0) / 100,
                issues=data.get("issues", []),
                feedback=data.get(
                    "feedback", ""
                ),
            )
        except (
            json.JSONDecodeError,
            KeyError,
        ):
            # 解析失败时的 fallback
            verify_result = VerifyResult(
                passed=False,
                score=0.5,
                issues=["verify_parse_error"],
                feedback=response.strip(),
            )

        logger.info(
            f"[VerifyAgent] "
            f"score={verify_result.score:.0%} "
            f"passed={verify_result.passed} "
            f"issues={verify_result.issues}"
        )

        # 存入 context 供后续 Agent 使用
        context.set(
            "verify_result", verify_result
        )
        context.set(
            "verify_score",
            int(verify_result.score * 100),
        )

        # 兼容旧接口返回 AgentResult
        agent_result = AgentResult(
            success=verify_result.passed,
            content=verify_result.feedback,
            score=verify_result.score,
            metadata={
                "issues": verify_result.issues,
            },
        )
        context.set("verify", verify_result.feedback)

        await event_bus.publish(
            AGENT_COMPLETED,
            {"agent": "verify"},
        )

        return verify_result
