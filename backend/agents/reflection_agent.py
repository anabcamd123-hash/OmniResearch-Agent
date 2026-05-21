import asyncio
from backend.agents.base_agent import BaseAgent
from backend.agents.result import AgentResult
from backend.executor.context import ExecutionContext
from backend.utils.logger import logger
from backend.runtime.runtime_state import state
from backend.runtime.events import bus
from backend.storage.repository import MemoryRepository
from backend.llm.provider_factory import get_provider


class ReflectionAgent(BaseAgent):

    def __init__(self):
        self.llm = get_provider()
        self.memory_repo = MemoryRepository()

    async def run(
        self,
        task: str,
        context: ExecutionContext,
    ):

        state.agent_status["reflection"] = "running"
        state.timeline.append({
            "agent": "Reflection",
            "event": "started",
        })

        await bus.publish("agent_started", {
            "agent": "reflection",
            "task": task[:50],
        })

        logger.info(
            "[ReflectionAgent] Evaluating..."
        )

        # Read all previous context
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

Decide:
1. Is this result correct and complete?
2. If not, why?
3. Should we retry?

Return format:
need_retry: true/false
reason: <one sentence explanation>
"""

        output = await asyncio.to_thread(
            self.llm.invoke, prompt
        )

        need_retry = "true" in output.lower()
        reason = output.strip()

        # Save learning
        await self.save_learning(
            task, reason, need_retry
        )

        result = AgentResult(
            success=not need_retry,
            content=reason,
            metadata={"need_retry": need_retry},
        )

        # Save to context
        context.set("reflection", result.content)

        logger.info(
            f"[ReflectionAgent] "
            f"retry={need_retry}"
        )

        state.agent_status["reflection"] = "completed"
        state.timeline.append({
            "agent": "Reflection",
            "event": "completed",
        })

        await bus.publish("agent_completed", {
            "agent": "reflection",
            "result": result.to_dict(),
        })

        return result

    async def save_learning(
        self, task, reason, need_retry
    ):

        memory_type = (
            "success"
            if not need_retry
            else "failure"
        )

        summary_prompt = f"""
Summarize this experience in one sentence.

Task: {task}
Feedback: {reason}
Outcome: {memory_type}

Return one sentence of knowledge.
"""

        knowledge = await asyncio.to_thread(
            self.llm.invoke, summary_prompt
        )

        await self.memory_repo.add_memory(
            content=knowledge.strip(),
            source="learning",
            memory_type=memory_type,
        )
