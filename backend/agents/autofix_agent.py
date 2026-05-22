"""
AutoFixAgent - 自动修复 Agent

输入: 原始代码 + VerifyResult + ReflectionResult
输出: 修复后的代码

闭环:
  Coding → Verify → Reflection → AutoFix → Coding → Verify ...
"""

import asyncio
from dataclasses import dataclass

from backend.agents.base_agent import BaseAgent
from backend.executor.context import ExecutionContext
from backend.utils.logger import logger, log_tokens
from backend.runtime.event_bus import event_bus
from backend.runtime.event_types import (
    AGENT_STARTED,
    AGENT_COMPLETED,
)
from backend.llm.provider_factory import get_provider

llm = get_provider()


@dataclass
class AutoFixResult:
    fixed_code: str
    explanation: str


class AutoFixAgent(BaseAgent):

    async def run(
        self,
        task: str,
        context: ExecutionContext,
    ):
        """
        task: 不使用（接口兼容）
        context: 需包含 coding, verify_result, reflection_result
        """

        await event_bus.publish(
            AGENT_STARTED,
            {"agent": "autofix"},
        )

        logger.info("[AutoFixAgent] Fixing code...")

        code = context.get("coding", "")
        verify_result = context.get(
            "verify_result", None
        )
        reflection_result = context.get(
            "reflection_result", None
        )

        issues = ""
        feedback = ""
        root_cause = ""
        suggestion = ""

        if verify_result:
            issues = ", ".join(
                verify_result.issues
            )
            feedback = verify_result.feedback

        if reflection_result:
            root_cause = reflection_result.root_cause
            suggestion = reflection_result.suggestion

        prompt = f"""
Fix this Python code.

Original Code:
{code}

Issues Found:
{issues or "none"}

Feedback:
{feedback or "none"}

Root Cause:
{root_cause or "unknown"}

Suggestion:
{suggestion or "none"}

Requirements:
- Preserve original functionality
- Fix all identified issues
- Include proper error handling
- Include a print() statement for output
- Return ONLY the Python code
- No markdown, no explanation
"""

        fixed_code = await asyncio.to_thread(
            llm.invoke, prompt
        )

        fixed_code = self._clean_code(fixed_code)

        log_tokens(200)

        logger.info(
            "[AutoFixAgent] Code fixed, "
            f"{len(fixed_code)} chars"
        )

        result = AutoFixResult(
            fixed_code=fixed_code,
            explanation=(
                f"Fixed: {issues or 'general'}"
            ),
        )

        await event_bus.publish(
            AGENT_COMPLETED,
            {"agent": "autofix"},
        )

        return result

    def _clean_code(self, code: str) -> str:
        if "```" in code:
            lines = code.split("\n")
            code_lines = []
            in_block = False
            for line in lines:
                if line.strip().startswith("```"):
                    in_block = not in_block
                    continue
                if in_block:
                    code_lines.append(line)
            code = "\n".join(code_lines)
        return code
