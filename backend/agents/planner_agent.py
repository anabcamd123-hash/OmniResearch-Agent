class PlannerAgent:

    def create_plan(self, task: str):

        return {
            "task": task,
            "subtasks": [
                "research",
                "generate_code",
                "verify"
            ]
        }
