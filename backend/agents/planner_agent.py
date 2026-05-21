from backend.executor.task import Task
from backend.utils.logger import stream_log
from backend.runtime.runtime_state import state
from backend.llm.provider_factory import get_provider

llm = get_provider()


def build_mermaid(tasks):

    lines = ["graph TD"]

    for task in tasks:

        for dep in task.dependencies:

            lines.append(
                f"    {dep} --> {task.task_id}"
            )

    if not any(t.dependencies for t in tasks):
        for i in range(len(tasks) - 1):
            lines.append(
                f"    {tasks[i].task_id} --> "
                f"{tasks[i + 1].task_id}"
            )

    return "\n".join(lines)


class PlannerAgent:

    async def create_plan(self, task: str):

        state.agent_status["planner"] = "running"

        state.timeline.append({
            "agent": "Planner",
            "event": "started"
        })

        await stream_log(
            f"[Planner] Creating DAG "
            f"workflow for: {task}"
        )

        prompt = f"""
Create a workflow plan for this task.

Task: {task}

Return ONLY a numbered list of steps.
Each step should be concise (3-8 words).
Use exactly 4 steps.
Format:
1. step one
2. step two
3. step three
4. step four
"""

        plan_text = llm.invoke(prompt)

        await stream_log(
            f"[Planner] LLM plan:\n{plan_text}"
        )

        # Parse steps from LLM response
        steps = []
        for line in plan_text.strip().split("\n"):
            line = line.strip()
            if line and line[0].isdigit():
                parts = line.split(".", 1)
                if len(parts) > 1:
                    steps.append(parts[1].strip())
                else:
                    steps.append(line)

        while len(steps) < 4:
            steps.append(
                f"Step {len(steps) + 1}"
            )

        steps = steps[:4]

        task_types = [
            "research", "coding",
            "verify", "reflection"
        ]

        tasks = []

        for i, (step, task_type) in enumerate(
            zip(steps, task_types)
        ):
            deps = []
            if i > 0:
                deps = [tasks[i - 1].task_id]

            tasks.append(
                Task(
                    task_id=task_type,
                    task_type=task_type,
                    dependencies=deps
                )
            )

        # Auto-generate Mermaid DAG
        state.current_dag = build_mermaid(tasks)

        await stream_log(
            f"[Planner] DAG created with "
            f"{len(tasks)} tasks"
        )

        state.agent_status["planner"] = (
            "completed"
        )

        state.timeline.append({
            "agent": "Planner",
            "event": "completed"
        })

        return tasks
