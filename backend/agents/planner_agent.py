from backend.executor.task import Task
from backend.utils.logger import stream_log
from backend.runtime.runtime_state import state


class PlannerAgent:

    async def create_plan(self, task: str):

        state.agent_status["planner"] = "running"

        state.timeline.append({
            "agent": "Planner",
            "event": "started"
        })

        await stream_log(
            f"[Planner] Creating DAG workflow for: {task}"
        )

        tasks = [

            Task(
                task_id="research",
                task_type="research"
            ),

            Task(
                task_id="coding",
                task_type="coding",
                dependencies=["research"]
            ),

            Task(
                task_id="verify",
                task_type="verify",
                dependencies=["coding"]
            ),

            Task(
                task_id="reflection",
                task_type="reflection",
                dependencies=["verify"]
            )
        ]

        state.current_dag = """
graph TD
    Research --> Coding
    Coding --> Verify
    Verify --> Reflection
"""

        await stream_log(
            f"[Planner] DAG created with {len(tasks)} tasks"
        )

        state.agent_status["planner"] = "completed"

        state.timeline.append({
            "agent": "Planner",
            "event": "completed"
        })

        return tasks
