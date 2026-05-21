import asyncio
from backend.agents.base_agent import BaseAgent
from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state
from backend.tools.python_runtime import PythonRuntime
from backend.llm.provider_factory import get_provider

runtime = PythonRuntime()
llm = get_provider()


class CodingResult:

    def __init__(
        self,
        code,
        language="python",
        execution=None,
    ):
        self.code = code
        self.language = language
        self.execution = execution or {}

    def to_dict(self):
        return {
            "code": self.code,
            "language": self.language,
            "execution": self.execution,
        }


class CodingAgent(BaseAgent):

    async def run(self, research_result):

        state.agent_status["coding"] = "running"

        state.timeline.append({
            "agent": "Coding",
            "event": "started"
        })

        logger.info(
            "[CodingAgent] Generating code..."
        )

        # Extract task info
        task_desc = ""
        if isinstance(research_result, dict):
            task_desc = research_result.get(
                "summary", str(research_result)
            )
        else:
            task_desc = str(research_result)

        # LLM generates code (async)
        prompt = f"""
Write Python code based on this task.

Task: {task_desc}

Requirements:
- Write complete, runnable code
- Include a print() statement for output
- Use only standard library
- Handle errors properly

Return ONLY the Python code.
No markdown, no explanation.
"""

        code = await asyncio.to_thread(
            llm.invoke, prompt
        )

        # Clean markdown code blocks
        code = self._clean_code(code)

        logger.info(
            "[CodingAgent] Executing code..."
        )

        # Execute code (async)
        execution_result = await asyncio.to_thread(
            runtime.execute, code
        )

        log_tokens(250)

        logger.info(
            f"[CodingAgent] Output: "
            f"{execution_result['stdout'].strip()}"
        )

        state.agent_status["coding"] = "completed"

        state.timeline.append({
            "agent": "Coding",
            "event": "completed"
        })

        return CodingResult(
            code=code,
            execution=execution_result,
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
