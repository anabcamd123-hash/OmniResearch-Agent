"""
PlannerAgent - JSON DAG 规划

输出 WorkflowPlan，支持并行/依赖/动态规划
LLM 失败时 fallback 到默认 4 步流水线
"""

import json
import asyncio

from backend.agents.planner_schema import (
    WorkflowPlan,
    PlanTask,
)
from backend.agents.registry import AGENT_REGISTRY
from backend.runtime.runtime_state import state
from backend.utils.logger import logger
from backend.rag.rag_service import rag_service
from backend.llm.provider_factory import get_provider

llm = get_provider()

# 默认 Plan，保证系统不因 LLM 失败而瘫痪
DEFAULT_PLAN = WorkflowPlan(
    tasks=[
        PlanTask(
            id="research_1",
            type="research",
            depends=[],
        ),
        PlanTask(
            id="coding_1",
            type="coding",
            depends=["research_1"],
        ),
        PlanTask(
            id="verify_1",
            type="verify",
            depends=["coding_1"],
        ),
        PlanTask(
            id="reflection_1",
            type="reflection",
            depends=["verify_1"],
        ),
    ]
)


class PlannerAgent:

    async def create_plan(
        self, task: str
    ) -> list[PlanTask]:
        state.agent_status["planner"] = "running"
        state.timeline.append(
            {"agent": "Planner", "event": "started"}
        )
        logger.info(
            f"[Planner] Creating DAG for: {task}"
        )

        try:
            rag_context = await rag_service.query(
                task, top_k=3
            )
            context_text = ""
            if rag_context:
                context_text = (
                    "Historical context:\n"
                    + "\n---\n".join(rag_context)
                )

            # 动态获取可用 agent 类型
            available = list(AGENT_REGISTRY.keys())
            types_desc = ", ".join(available)

            prompt = f"""
Create a JSON workflow plan for this task.

{context_text if context_text else ""}

Task: {task}

Available types: {types_desc}

Return ONLY valid JSON:
{{
  "tasks": [
    {{"id": "task1", "type": "research", "depends": []}},
    ...
  ]
}}

Requirements:
- 2-6 steps
- Unique ids
- Types from available list only
- Valid dependencies (no cycles)
"""

            plan_text = await asyncio.to_thread(
                llm.invoke, prompt
            )
            logger.info(
                f"[Planner] LLM plan:\n"
                f"{plan_text[:200]}"
            )

            # 清理 markdown 代码块
            text = plan_text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])

            plan_json = json.loads(text)
            plan = WorkflowPlan(**plan_json)

            # 验证 agent 类型
            valid = [
                t
                for t in plan.tasks
                if t.type in AGENT_REGISTRY
            ]
            if not valid:
                raise ValueError(
                    "No valid tasks"
                )
            plan = WorkflowPlan(
                tasks=valid[:6]
            )

        except Exception as e:
            logger.warning(
                f"[Planner] Failed: {e}. "
                f"Using default plan."
            )
            plan = DEFAULT_PLAN

        # 更新 DAG 可视化
        state.current_dag = self.build_mermaid(
            plan.tasks
        )

        state.agent_status["planner"] = "completed"
        state.timeline.append(
            {
                "agent": "Planner",
                "event": "completed",
            }
        )

        logger.info(
            f"[Planner] DAG: {len(plan.tasks)} tasks"
        )

        return plan.tasks

    @staticmethod
    def build_mermaid(
        tasks: list[PlanTask],
    ) -> str:
        lines = ["graph TD"]
        for task in tasks:
            for dep in task.depends:
                lines.append(
                    f"    {dep} --> {task.id}"
                )
        if not any(t.depends for t in tasks):
            for i in range(len(tasks) - 1):
                lines.append(
                    f"    {tasks[i].id} --> "
                    f"{tasks[i + 1].id}"
                )
        return "\n".join(lines)
