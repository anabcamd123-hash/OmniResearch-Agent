from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state
from backend.llm.provider_factory import get_provider

llm = get_provider()


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

        log_tokens(50)

        logger.info(
            f"[VerifyAgent] Score: {score}/100"
        )

        state.agent_status["verify"] = "completed"

        state.timeline.append({
            "agent": "Verify",
            "event": "completed"
        })

        return {
            "success": success,
            "score": score / 100,
            "evaluation": evaluation
        }
