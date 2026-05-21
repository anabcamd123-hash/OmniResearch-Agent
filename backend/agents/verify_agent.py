import re
import asyncio
from backend.agents.base_agent import BaseAgent
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
    ):

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

Score 0-100 based on:
- Correctness
- Completeness
- Relevance

Format:
Score: <number>
Reason: <one sentence>
Pass: yes/no
"""

        evaluation = await asyncio.to_thread(
            llm.invoke, prompt
        )

        score = 75
        match = re.search(
            r"score[:\s]*(\d+)",
            evaluation.lower()
        )
        if match:
            score = int(match.group(1))

        score = min(max(score, 0), 100)
        passed = score >= 70
        log_tokens(50)

        logger.info(
            f"[VerifyAgent] Score: {score}/100 "
            f"{'PASS' if passed else 'FAIL'}"
        )

        result = AgentResult(
            success=passed,
            content=evaluation.strip(),
            score=score / 100,
        )

        context.set("verify", result.content)
        context.set("verify_score", score)

        await event_bus.publish(
            AGENT_COMPLETED,
            {"agent": "verify"},
        )

        return result
