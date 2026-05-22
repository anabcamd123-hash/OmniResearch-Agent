"""
ReflectionAgent — 闭环自修复 + 学习

判断是否需要重试，保存经验到 Memory
"""

import asyncio

from backend.runtime.runtime_state import state
from backend.storage.repository import (
    MemoryRepository,
)
from backend.llm.provider_factory import get_provider
from backend.utils.logger import logger

llm = get_provider()


class ReflectionResult:

    def __init__(
        self,
        need_retry: bool,
        reason: str,
    ):
        self.need_retry = need_retry
        self.reason = reason


class ReflectionAgent:

    def __init__(self):
        self.memory_repo = MemoryRepository()

    async def run(self, task_desc, verify_result):
        state.agent_status["reflection"] = (
            "running"
        )
        state.timeline.append(
            {
                "agent": "Reflection",
                "event": "started",
            }
        )
        logger.info("[Reflection] Evaluating...")

        # 提取 verify 信息
        if hasattr(verify_result, "feedback"):
            feedback = verify_result.feedback
            passed = verify_result.passed
        elif isinstance(verify_result, dict):
            feedback = verify_result.get(
                "feedback", ""
            )
            passed = verify_result.get(
                "passed", False
            )
        else:
            feedback = str(verify_result)
            passed = False

        prompt = f"""
Task: {task_desc}
Result passed: {passed}
Feedback: {feedback}

Is the result good enough?
Reply with exactly one word: true (needs retry) or false (good enough)
"""

        output = await asyncio.to_thread(
            llm.invoke, prompt
        )

        need_retry = "true" in output.lower()
        reason = output.strip()

        # 保存学习经验
        memory_type = (
            "failure" if need_retry else "success"
        )
        try:
            await self.memory_repo.add_memory(
                content=(
                    f"TASK: {task_desc}\n"
                    f"FEEDBACK: {reason}"
                ),
                source="reflection",
                memory_type=memory_type,
            )
        except Exception:
            pass

        logger.info(
            f"[Reflection] retry={need_retry}"
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

        return ReflectionResult(
            need_retry=need_retry, reason=reason
        )
