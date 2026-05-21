from backend.utils.logger import logger
from backend.runtime.runtime_state import state

class ReflectionAgent:

    def run(self, verify_result):

        state.agent_status["reflection"] = "running"

        logger.info("[ReflectionAgent] Evaluating result quality...")

        if verify_result["score"] < 0.85:

            logger.info("[ReflectionAgent] Low score detected")

            state.agent_status["reflection"] = "completed"

            return {
                "reflection": "Task needs retry"
            }

        logger.info("[ReflectionAgent] Result accepted")

        state.agent_status["reflection"] = "completed"

        return {
            "reflection": "Task successful"
        }
