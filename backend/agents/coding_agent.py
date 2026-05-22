"""
CodingAgent — 代码生成 + 执行 + 自动重试

LLM 生成代码 → 子进程执行 → 异常捕获
"""

import asyncio

from backend.runtime.runtime_state import state
from backend.llm.provider_factory import get_provider
from backend.tools.python_sandbox import (
    python_sandbox,
)
from backend.utils.logger import logger

llm = get_provider()

MAX_RETRIES = 2


class CodingResult:

    def __init__(
        self,
        code: str,
        execution: dict = None,
        success: bool = True,
    ):
        self.code = code
        self.execution = execution or {}
        self.success = success

    def to_dict(self):
        return {
            "code": self.code,
            "execution": self.execution,
            "success": self.success,
        }


class CodingAgent:

    async def run(self, research_result):
        attempt = 0

        while attempt <= MAX_RETRIES:
            try:
                state.agent_status["coding"] = (
                    "running"
                )
                state.timeline.append(
                    {
                        "agent": "Coding",
                        "event": (
                            f"started "
                            f"(attempt {attempt + 1})"
                        ),
                    }
                )
                logger.info(
                    f"[Coding] Generating, "
                    f"attempt {attempt + 1}"
                )

                # 提取任务描述
                if isinstance(
                    research_result, dict
                ):
                    task_desc = (
                        research_result.get(
                            "summary",
                            str(research_result),
                        )
                    )
                else:
                    task_desc = str(
                        research_result
                    )

                prompt = f"""
Write Python code for this task.

Task: {task_desc}

Requirements:
- Complete, runnable code
- Include print() for output
- Use only standard library
- Handle errors properly

Return ONLY Python code.
"""

                code = await asyncio.to_thread(
                    llm.invoke, prompt
                )
                code = self._clean_code(code)

                # 执行
                exec_result = (
                    await python_sandbox.execute(
                        code
                    )
                )

                if not exec_result.success:
                    raise RuntimeError(
                        exec_result.error
                        or "Execution failed"
                    )

                logger.info(
                    "[Coding] Output: "
                    + exec_result.content.strip()
                )

                state.agent_status["coding"] = (
                    "completed"
                )
                state.timeline.append(
                    {
                        "agent": "Coding",
                        "event": "completed",
                    }
                )

                return CodingResult(
                    code=code,
                    execution={
                        "stdout": (
                            exec_result.content
                        ),
                        "stderr": "",
                    },
                    success=True,
                )

            except Exception as e:
                attempt += 1
                logger.error(
                    f"[Coding] Error: {e}, "
                    f"attempt {attempt}"
                )

                if attempt > MAX_RETRIES:
                    state.agent_status["coding"] = (
                        "failed"
                    )
                    state.timeline.append(
                        {
                            "agent": "Coding",
                            "event": "failed",
                        }
                    )
                    return CodingResult(
                        code="",
                        execution={
                            "error": str(e)
                        },
                        success=False,
                    )

    def _clean_code(self, code: str) -> str:
        if "```" in code:
            lines = code.split("\n")
            code_lines = []
            in_block = False
            for line in lines:
                if line.strip().startswith("```"):
                    in_block = not in_block
                    continue
                if in_block:
                    code_lines.append(line)
            return "\n".join(code_lines)
        return code
