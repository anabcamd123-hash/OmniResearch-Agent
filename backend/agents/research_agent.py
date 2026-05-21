from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state

class ResearchAgent:

    def run(self, task: str):

        state.agent_status["research"] = "running"

        state.timeline.append({
            "agent": "Research",
            "event": "started"
        })

        logger.info("[ResearchAgent] Searching knowledge base...")

        result = {
            "summary": f"Research completed for: {task}",
            "references": [
                "Transformer Paper",
                "Attention Is All You Need"
            ]
        }

        log_tokens(120)

        logger.info("[ResearchAgent] Research completed")

        state.agent_status["research"] = "completed"

        state.timeline.append({
            "agent": "Research",
            "event": "completed"
        })

        return result
