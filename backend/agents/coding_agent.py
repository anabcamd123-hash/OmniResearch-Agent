from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state
from backend.tools.python_runtime import PythonRuntime

runtime = PythonRuntime()

class CodingAgent:

    def run(self, research_result):

        state.agent_status["coding"] = "running"

        state.timeline.append({
            "agent": "Coding",
            "event": "started"
        })

        logger.info("[CodingAgent] Generating code...")

        code = """
def add(a, b):
    return a + b

print(add(1, 2))
"""

        logger.info("[CodingAgent] Executing code...")

        execution_result = runtime.execute(code)

        log_tokens(250)

        logger.info(
            f"[CodingAgent] Execution "
            f"{'success' if execution_result['success'] else 'failed'}: "
            f"{execution_result['stdout'].strip()}"
        )

        state.agent_status["coding"] = "completed"

        state.timeline.append({
            "agent": "Coding",
            "event": "completed"
        })

        return {
            "code": code,
            "execution": execution_result
        }
