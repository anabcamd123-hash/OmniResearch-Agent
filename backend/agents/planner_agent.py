import json
import asyncio
from backend.agents.base_agent import BaseAgent
from backend.executor.task import Task
from backend.executor.context import ExecutionContext
from backend.utils.logger import logger
from backend.runtime.event_bus import event_bus
from backend.runtime.event_types import (
    AGENT_STARTED,
    AGENT_COMPLETED,
)
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

    async def run(
        self,
        task: str,
        context: ExecutionContext = None,
    ):

        await event_bus.publish(
            AGENT_STARTED,
            {"agent": "planner", "task": task},
        )

        logger.info(
            f"[Planner] Creating plan for: {task}"
        )

        rag_context = await rag_service.query(
            task, top_k=3
        )

        context_text = ""
        if rag_context:
            context_text = (
                "Historical context:\n"
                + "\n---\n".join(rag_context)
            )

        prompt = f"""
You are a workflow planner.

{context_text if context_text else ""}

Task: {task}

Available agent types:
- research: Search, analyze, gather info
- coding: Generate and execute code
- verify: Evaluate result quality
- reflection: Analyze and suggest improvements

Return a JSON array of steps.
Each step: {{"task": "<desc>", "agent": "<type>"}}
Use 2-5 steps.

Return ONLY the JSON array.
"""

        plan_text = await asyncio.to_thread(
            llm.invoke, prompt
        )

        logger.info(
            f"[Planner] LLM plan:\n{plan_text}"
        )

        steps = self._parse_plan(plan_text)

        tasks = []

        for i, step in enumerate(steps):
            deps = []
            if i > 0:
                deps = [tasks[i - 1].task_id]

            task_id = f"step_{i}_{step['agent']}"

            tasks.append(
                Task(
                    task_id=task_id,
                    task_type=step["agent"],
                    dependencies=deps,
                    payload=step.get("task", ""),
                )
            )

        state.current_dag = build_mermaid(tasks)

        logger.info(
            f"[Planner] DAG created with "
            f"{len(tasks)} tasks"
        )

        await event_bus.publish(
            AGENT_COMPLETED,
            {"agent": "planner"},
        )

        return tasks

    def _parse_plan(self, plan_text: str):

        try:
            text = plan_text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])
            steps = json.loads(text)
            if isinstance(steps, list):
                return steps[:5]
        except json.JSONDecodeError:
            pass

        return [
            {"task": "Research", "agent": "research"},
            {"task": "Generate code", "agent": "coding"},
            {"task": "Verify", "agent": "verify"},
            {"task": "Reflect", "agent": "reflection"},
        ]
