from backend.agents.coding_agent import CodingAgent
from backend.agents.verify_agent import VerifyAgent
from backend.agents.reflection_agent import ReflectionAgent
from backend.utils.logger import stream_log


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

        code = await self.coder.run(objective)

        retry = 0

        while retry < self.MAX_RETRY:

            verify = await self.verifier.run(code)

            if verify.passed:
                await stream_log(
                    f"[AutoFix] success after "
                    f"{retry} retries"
                )

                return code

            await stream_log(
                f"[AutoFix] verify failed, "
                f"retry {retry + 1}"
            )

            reflection = await self.reflector.run(
                str(code.to_dict()), code
            )

            code = await self.coder.run(
                f"""
Objective:
{objective}

Previous code:
{code.code}

Fix based on feedback:
{reflection.reason}

{verify.feedback}
"""
            )

            retry += 1

        raise Exception(
            f"AutoFix failed after "
            f"{self.MAX_RETRY} retries"
        )
