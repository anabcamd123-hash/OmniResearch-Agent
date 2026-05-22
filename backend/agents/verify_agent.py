"""
VerifyAgent — 评分 + 反馈

LLM 评估结果质量，返回结构化评分
"""

import asyncio

from backend.runtime.runtime_state import state
from backend.llm.provider_factory import get_provider
from backend.utils.logger import logger

llm = get_provider()


class VerifyResult:

    def __init__(
        self,
        passed: bool,
        score: float,
        feedback: str,
    ):
        self.passed = passed
        self.score = score
        self.feedback = feedback

    def to_dict(self):
        return {
            "passed": self.passed,
            "score": self.score,
            "feedback": self.feedback,
        }


class VerifyAgent:

    async def run(self, coding_result):
        state.agent_status["verify"] = "running"
        state.timeline.append(
            {
                "agent": "Verify",
                "event": "started",
            }
        )
        logger.info("[Verify] Evaluating...")

        # 提取代码
        if hasattr(coding_result, "code"):
            code = coding_result.code
        elif isinstance(coding_result, dict):
            code = coding_result.get("code", "")
        else:
            code = str(coding_result)

        prompt = f"""
Evaluate this code result.

Code:
{code}

Score 0-100 based on:
- Correctness
- Completeness
- Relevance

Return format:
Score: <number>
Pass: yes/no
Reason: <one sentence>
"""

        evaluation = await asyncio.to_thread(
            llm.invoke, prompt
        )

        # 解析分数
        score = 75
        try:
            import re

            match = re.search(
                r"score[:\s]*(\d+)",
                evaluation.lower(),
            )
            if match:
                score = int(match.group(1))
                score = min(max(score, 0), 100)
        except Exception:
            pass

        passed = score >= 70

        logger.info(
            f"[Verify] Score: {score}/100 "
            f"{'PASS' if passed else 'FAIL'}"
        )

        state.agent_status["verify"] = "completed"
        state.timeline.append(
            {
                "agent": "Verify",
                "event": "completed",
            }
        )

        return VerifyResult(
            passed=passed,
            score=score / 100,
            feedback=evaluation.strip(),
        )
