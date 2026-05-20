from backend.utils.logger import stream_log

class PlannerAgent:

    async def create_plan(self, task: str):

        await stream_log(f"[Planner] Received task: {task}")

        subtasks = [
            "research",
            "generate_code",
            "verify"
        ]

        await stream_log(
            f"[Planner] Created {len(subtasks)} subtasks"
        )

        return {
            "task": task,
            "subtasks": subtasks
        }
