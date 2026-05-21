from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state

class CodingAgent:

    def run(self, research_result):

        state.agent_status["coding"] = "running"

        logger.info("[CodingAgent] Generating code...")

        code = '''
def train():
    print("training model")
'''

        log_tokens(250)

        logger.info("[CodingAgent] Code generation completed")

        state.agent_status["coding"] = "completed"

        return {
            "code": code
        }
