from backend.utils.logger import logger
from backend.runtime.runtime_state import state
from backend.llm.provider_factory import get_provider

llm = get_provider()


class ReflectionAgent:

    def run(self, verify_result):

        state.agent_status["reflection"] = "running"

        state.timeline.append({
            "agent": "Reflection",
            "event": "started"
        })

        logger.info(
            "[ReflectionAgent] "
            "Evaluating workflow..."
        )

        # Handle VerifyResult or dict
        if hasattr(verify_result, "score"):
            score = verify_result.score
            feedback = verify_result.feedback
        else:
            score = verify_result.get("score", 0)
            feedback = verify_result.get(
                "evaluation", "N/A"
            )

        # LLM reflection
        reflection = llm.invoke(
            f"""
Analyze this workflow execution.

Verification Score: {score}

Details:
{feedback}

Provide:
1. What went well
2. What can improve
3. Specific suggestions

Be concise, use bullet points.
"""
        )

        logger.info(
            f"[ReflectionAgent] {reflection}"
        )

        state.agent_status["reflection"] = (
            "completed"
        )

        state.timeline.append({
            "agent": "Reflection",
            "event": "completed"
        })

        return {
            "reflection": reflection,
            "verdict": "success"
            if score >= 0.85
            else "needs_retry",
        }
