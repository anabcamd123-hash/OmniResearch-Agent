import json
import asyncio
from backend.agents.base_agent import BaseAgent
from backend.executor.task import Task
from backend.utils.logger import stream_log
from backend.runtime.runtime_state import state
from backend.rag.rag_service import rag_service
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


class PlannerAgent(BaseAgent):

    async def run(self, task: str):

        state.agent_status["planner"] = "running"

        state.timeline.append({
            "agent": "Planner",
            "event": "started"
        })

        await stream_log(
            f"[Planner] Creating plan for: {task}"
        )

        # RAG context
        rag_context = await rag_service.query(
            task, top_k=3
        )

        context_text = ""
        if rag_context:
            context_text = (
                "Historical context:\n"
                + "\n---\n".join(rag_context)
            )

        # LLM dynamic plan generation
        prompt = f"""
You are a workflow planner.

{context_text if context_text else ""}

Task: {task}

Available agent types:
- research: Search, analyze, gather information
- coding: Generate and execute code
- verify: Evaluate result quality
- reflection: Analyze and suggest improvements

Return a JSON array of steps.
Each step: {{"task": "<description>", "agent": "<agent_type>"}}
Use 2-5 steps. Match agents to task needs.

Example for "Analyze PDF":
[
  {{"task": "Parse and extract PDF content", "agent": "research"}},
  {{"task": "Summarize key findings", "agent": "research"}},
  {{"task": "Verify completeness", "agent": "verify"}}
]

Return ONLY the JSON array.
"""

        plan_text = await asyncio.to_thread(
            llm.invoke, prompt
        )

        await stream_log(
            f"[Planner] LLM plan:\n{plan_text}"
        )

        # Parse JSON plan
        steps = self._parse_plan(plan_text)

        # Build tasks from steps
        tasks = []

        for i, step in enumerate(steps):
            deps = []
            if i > 0:
                deps = [tasks[i - 1].task_id]

            task_id = (
                f"step_{i}_"
                f"{step['agent']}"
            )

            tasks.append(
                Task(
                    task_id=task_id,
                    task_type=step["agent"],
                    dependencies=deps,
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

    def _parse_plan(self, plan_text: str):

        # Try JSON parse
        try:
            # Extract JSON from text
            text = plan_text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])

            steps = json.loads(text)

            if isinstance(steps, list):
                return steps[:5]
        except json.JSONDecodeError:
            pass

        # Fallback: fixed plan
        return [
            {
                "task": "Research and gather info",
                "agent": "research"
            },
            {
                "task": "Generate code",
                "agent": "coding"
            },
            {
                "task": "Verify result",
                "agent": "verify"
            },
            {
                "task": "Reflect and improve",
                "agent": "reflection"
            },
        ]
