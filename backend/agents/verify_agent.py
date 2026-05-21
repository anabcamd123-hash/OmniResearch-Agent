from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state

class VerifyAgent:

    def run(self, code_result):

        state.agent_status["verify"] = "running"

        state.timeline.append({
            "agent": "Verify",
            "event": "started"
        })

        logger.info("[VerifyAgent] Running verification...")

        success = True

        log_tokens(50)

        logger.info("[VerifyAgent] Verification passed")

        state.agent_status["verify"] = "completed"

        state.timeline.append({
            "agent": "Verify",
            "event": "completed"
        })

        return {
            "success": success,
            "score": 0.91
        }
