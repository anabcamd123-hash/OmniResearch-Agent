from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state
from backend.llm.provider_factory import get_provider

llm = get_provider()


class VerifyResult:

    def __init__(
        self,
        passed: bool,
        feedback: str,
        score: float = 0,
    ):
        self.passed = passed
        self.feedback = feedback
        self.score = score

    def to_dict(self):
        return {
            "passed": self.passed,
            "feedback": self.feedback,
            "score": self.score,
        }


class VerifyAgent:

    def run(self, code_result):

        state.agent_status["verify"] = "running"

        state.timeline.append({
            "agent": "Verify",
            "event": "started"
        })

        logger.info(
            "[VerifyAgent] Running verification..."
        )

        # Handle CodingResult or dict
        if hasattr(code_result, "code"):
            code = code_result.code
            execution = code_result.execution
        else:
            code = code_result.get("code", "")
            execution = code_result.get(
                "execution", {}
            )

        output = execution.get("stdout", "")
        stderr = execution.get("stderr", "")
        success = execution.get("success", False)

        # LLM evaluation
        evaluation = llm.invoke(
            f"""
Evaluate this code execution result.

Code:
{code}

Output:
{output}

Errors:
{stderr}

Execution Success: {success}

Score 0-100 based on:
- Code correctness
- Output validity
- Error handling

Format:
Score: <number>
Reason: <one sentence>
Pass: yes/no
"""
        )

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

        # Determine pass/fail
        passed = success and score >= 70

        feedback = evaluation.strip()

        log_tokens(50)

        logger.info(
            f"[VerifyAgent] Score: {score}/100 "
            f"{'PASS' if passed else 'FAIL'}"
        )

        state.agent_status["verify"] = "completed"

        state.timeline.append({
            "agent": "Verify",
            "event": "completed"
        })

        return VerifyResult(
            passed=passed,
            feedback=feedback,
            score=score / 100,
        )
