"""
PlannerAgent — 任务分解 + DAG 生成

输入任务描述，输出 Task 列表（含依赖关系）
"""

from backend.executor.task import Task
from backend.runtime.runtime_state import state
from backend.rag.rag_service import rag_service
from backend.llm.provider_factory import get_provider
from backend.utils.logger import logger

try:
    llm = get_provider()
except Exception:
    llm = None  # lazy: tests mock this


def build_mermaid(tasks):
    lines = ["graph TD"]
    for task in tasks:
        for dep in task.dependencies:
            lines.append(f"    {dep} --> {task.task_id}")
    if not any(t.dependencies for t in tasks):
        for i in range(len(tasks) - 1):
            lines.append(
                f"    {tasks[i].task_id} --> "
                f"{tasks[i + 1].task_id}"
            )
    return "\n".join(lines)


# 默认 4 步流水线
DEFAULT_STEPS = [
    ("research", "research"),
    ("coding", "coding"),
    ("verify", "verify"),
    ("reflection", "reflection"),
]


class PlannerAgent:

    async def create_plan(self, task_desc: str):
        state.agent_status["planner"] = "running"
        state.timeline.append(
            {"agent": "Planner", "event": "started"}
        )
        logger.info(
            f"[Planner] Creating DAG for: "
            f"{task_desc[:50]}"
        )

        # 查询历史知识
        rag_context = ""
        try:
            rag_results = await rag_service.query(
                task_desc, top_k=3
            )
            if rag_results:
                rag_context = (
                    "Historical context:\n"
                    + "\n---\n".join(rag_results)
                )
        except Exception:
            pass

        # LLM 生成计划
        prompt = f"""
Create a workflow plan for this task.

{rag_context if rag_context else ""}

Task: {task_desc}

Available agent types:
- research: Search and gather information
- coding: Generate and execute code
- verify: Evaluate result quality
- reflection: Analyze and suggest improvements

Return ONLY a JSON array of steps:
[
  {{"step": "description", "agent": "research"}},
  {{"step": "description", "agent": "coding"}},
  ...
]

Use 2-5 steps. Each agent type from available list.
"""

        try:
            plan_text = llm.invoke(prompt)
            import json

            text = plan_text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                text = "\n".join(lines[1:-1])

            steps = json.loads(text)
            if not isinstance(steps, list):
                raise ValueError("not a list")

            # 验证 agent 类型
            valid_types = {
                "research",
                "coding",
                "verify",
                "reflection",
            }
            steps = [
                s
                for s in steps
                if s.get("agent") in valid_types
            ][:5]

            if not steps:
                raise ValueError("no valid steps")

        except Exception as e:
            logger.warning(
                f"[Planner] LLM failed: {e}, "
                f"using default"
            )
            steps = [
                {"step": s[0], "agent": s[1]}
                for s in DEFAULT_STEPS
            ]

        # 构建 Task 列表
        tasks = []
        for i, step in enumerate(steps):
            agent_type = step["agent"]
            deps = (
                [tasks[i - 1].task_id]
                if i > 0
                else []
            )
            tasks.append(
                Task(
                    task_id=agent_type,
                    task_type=agent_type,
                    dependencies=deps,
                )
            )

        state.current_dag = build_mermaid(tasks)
        state.agent_status["planner"] = "completed"
        state.timeline.append(
            {
                "agent": "Planner",
                "event": "completed",
            }
        )

        logger.info(
            f"[Planner] DAG: {len(tasks)} tasks"
        )

        return tasks
