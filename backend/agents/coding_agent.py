"""
CodingAgent — 代码生成 + 自动重试 + 异常捕获
"""

import asyncio
from dataclasses import dataclass

from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state
from backend.tools.python_sandbox import python_sandbox
from backend.tools.result import ToolResult
from backend.llm.provider_factory import get_provider

llm = get_provider()


@dataclass
class CodingResult:
    code: str
    language: str = "python"
    execution: dict = None
    success: bool = True

    def to_dict(self):
        return {
            "code": self.code,
            "language": self.language,
            "execution": self.execution or {},
        }


class CodingAgent:

    MAX_RETRIES = 2

    async def run(self, research_result):
        attempt = 0

        while attempt <= self.MAX_RETRIES:
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
                    f"[CodingAgent] Generating, "
                    f"attempt {attempt + 1}..."
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
Write Python code based on this task.

Task: {task_desc}

Requirements:
- Complete runnable code
- Include a print() statement for output
- Use only standard library
- Handle errors properly

Return ONLY Python code.
"""

                code = await asyncio.to_thread(
                    llm.invoke, prompt
                )
                code = self._clean_code(code)

                # 执行代码
                logger.info(
                    "[CodingAgent] Executing..."
                )
                exec_result = (
                    await python_sandbox.execute(
                        code
                    )
                )
                log_tokens(250)

                if exec_result.success:
                    logger.info(
                        "[CodingAgent] Output: "
                        + exec_result.content.strip()
                    )
                else:
                    raise RuntimeError(
                        exec_result.error
                        or "Execution failed"
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
                        "stderr": (
                            exec_result.error
                            or ""
                        ),
                    },
                    success=True,
                )

            except Exception as e:
                attempt += 1
                logger.error(
                    f"[CodingAgent] Error: {e}, "
                    f"attempt {attempt}"
                )

                if attempt > self.MAX_RETRIES:
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

    def _clean_code(self, code):
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
            code = "\n".join(code_lines)
        return code
