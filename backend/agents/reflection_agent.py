from backend.utils.logger import logger

class ReflectionAgent:

    def run(self, verify_result):

        logger.info("[ReflectionAgent] Evaluating result quality...")

        if verify_result["score"] < 0.85:

            logger.info("[ReflectionAgent] Low score detected")

            return {
                "reflection": "Task needs retry"
            }

        logger.info("[ReflectionAgent] Result accepted")

        return {
            "reflection": "Task successful"
        }
