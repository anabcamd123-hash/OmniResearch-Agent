from backend.utils.logger import logger

class PlannerAgent:

    def create_plan(self, task: str):

        logger.info(f\"[Planner] Received task: {task}\")

        subtasks = [
            "research",
            "generate_code",
            "verify"
        ]

        logger.info(f\"[Planner] Created {len(subtasks)} subtasks\")

        return {
            "task": task,
            "subtasks": subtasks
        }
