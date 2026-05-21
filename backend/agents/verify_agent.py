import re
import asyncio
from backend.agents.base_agent import BaseAgent
from backend.agents.result import AgentResult
from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state
from backend.runtime.events import bus
from backend.llm.provider_factory import get_provider

llm = get_provider()


class VerifyAgent(BaseAgent):

    async def run(self, result):

        state.agent_status["verify"] = "running"
        state.timeline.append({
            "agent": "Verify", "event": "started",
        })

        await bus.publish("agent_started", {
            "agent": "verify", "task": "evaluating",
        })

        logger.info("[VerifyAgent] Evaluating...")

        prompt = f"""
Evaluate this result quality.

Result:
{result}

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

        state.agent_status["verify"] = "completed"
        state.timeline.append({
            "agent": "Verify", "event": "completed",
        })

        agent_result = AgentResult(
            success=passed,
            content=evaluation.strip(),
            score=score / 100,
        )

        await bus.publish("agent_completed", {
            "agent": "verify",
            "result": agent_result.to_dict(),
        })

        return agent_result
