from backend.utils.logger import logger
from backend.runtime.runtime_state import state
from backend.storage.repository import MemoryRepository
from backend.llm.provider_factory import get_provider


class ReflectionResult:

    def __init__(
        self,
        need_retry: bool,
        reason: str,
    ):
        self.need_retry = need_retry
        self.reason = reason

    def to_dict(self):
        return {
            "need_retry": self.need_retry,
            "reason": self.reason,
        }


class ReflectionAgent:

    def __init__(self):

        self.llm = get_provider()

        self.memory_repo = MemoryRepository()

    async def run(self, task: str, result):

        state.agent_status["reflection"] = "running"

        state.timeline.append({
            "agent": "Reflection",
            "event": "started",
        })

        logger.info(
            "[ReflectionAgent] Evaluating..."
        )

        prompt = f"""
You are a reflection system.

Task:
{task}

Result:
{result}

Decide:
1. Is this result correct and complete?
2. If not, why?
3. Should we retry?

Return format:
need_retry: true/false
reason: <one sentence explanation>
"""

        output = self.llm.invoke(prompt)

        need_retry = "true" in output.lower()

        reflection = ReflectionResult(
            need_retry=need_retry,
            reason=output.strip(),
        )

        # Save learning memory
        await self.save_learning(
            task, result, reflection
        )

        logger.info(
            f"[ReflectionAgent] "
            f"retry={need_retry}"
        )

        state.agent_status["reflection"] = (
            "completed"
        )

        state.timeline.append({
            "agent": "Reflection",
            "event": "completed",
        })

        return reflection

    async def save_learning(
        self,
        task,
        result,
        reflection: ReflectionResult,
    ):

        memory_type = (
            "success"
            if not reflection.need_retry
            else "failure"
        )

        content = (
            f"TASK: {task}\n"
            f"RESULT: {str(result)[:500]}\n"
            f"FEEDBACK: {reflection.reason}"
        )

        await self.memory_repo.add_memory(
            content=content,
            source="learning",
            memory_type=memory_type,
        )
