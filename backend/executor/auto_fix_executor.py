from backend.agents.coding_agent import CodingAgent
from backend.agents.verify_agent import VerifyAgent
from backend.agents.reflection_agent import ReflectionAgent
from backend.utils.logger import stream_log
from backend.runtime.runtime_state import state


class AutoFixExecutor:

    MAX_RETRY = 3

    def __init__(self):
        self.coder = CodingAgent()
        self.verifier = VerifyAgent()
        self.reflector = ReflectionAgent()

    async def run(self, objective: str):

        await stream_log(
            f"[AutoFix] Starting for: "
            f"{objective[:50]}..."
        )

        code = self.coder.run(objective)

        retry = 0

        while retry < self.MAX_RETRY:

            verify = self.verifier.run(code)

            if verify.passed:
                state.auto_fix_stats[
                    "success"
                ] += 1

                state.auto_fix_stats[
                    "total_retry"
                ] += retry

                await stream_log(
                    f"[AutoFix] success after "
                    f"{retry} retries"
                )

                return code

            await stream_log(
                f"[AutoFix] verify failed, "
                f"retry {retry + 1}"
            )

            state.auto_fix_stats[
                "total_retry"
            ] += 1

            feedback = self.reflector.run(
                {"code": code, "score": 0}
            )

            code = self.coder.run(
                f"""
Objective:
{objective}

Previous code:
{code.code}

Fix based on feedback:
{feedback.get('reflection', 'improve code')}

{verify.feedback}
"""
            )

            retry += 1

        state.auto_fix_stats["failed"] += 1

        raise Exception(
            f"AutoFix failed after "
            f"{self.MAX_RETRY} retries"
        )
