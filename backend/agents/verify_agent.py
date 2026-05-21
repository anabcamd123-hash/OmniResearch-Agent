from backend.tools.router import tool_router
from backend.agents.reflection_agent import ReflectionAgent
from backend.utils.logger import stream_log
from backend.runtime.runtime_state import state
from backend.utils.logger import logger, log_tokens
from backend.llm.provider_factory import get_provider

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

    def run(self, result):

        state.agent_status["verify"] = "running"

        state.timeline.append({
            "agent": "Verify",
            "event": "started",
        })

        logger.info(
            "[VerifyAgent] Evaluating result..."
        )

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

        evaluation = llm.invoke(prompt)

        # Parse score
        score = 75
        for line in evaluation.split("\n"):
            if "score" in line.lower():
                for word in line.split():
                    try:
                        score = int(word)
                        break
                    except ValueError:
                        continue

        score = min(max(score, 0), 100)

        passed = score >= 70

        log_tokens(50)

        logger.info(
            f"[VerifyAgent] Score: {score}/100 "
            f"{'PASS' if passed else 'FAIL'}"
        )

        state.agent_status["verify"] = "completed"

        state.timeline.append({
            "agent": "Verify",
            "event": "completed",
        })

        return VerifyResult(
            passed=passed,
            score=score / 100,
            feedback=evaluation.strip(),
        )
