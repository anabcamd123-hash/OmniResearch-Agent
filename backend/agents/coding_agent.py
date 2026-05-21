import asyncio
from backend.agents.base_agent import BaseAgent
from backend.agents.result import AgentResult
from backend.executor.context import ExecutionContext
from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state
from backend.runtime.events import bus
from backend.tools.python_runtime import PythonRuntime
from backend.llm.provider_factory import get_provider

runtime = PythonRuntime()
llm = get_provider()


class CodingAgent(BaseAgent):

    async def run(
        self,
        task: str,
        context: ExecutionContext,
    ):

        state.agent_status["coding"] = "running"
        state.timeline.append({
            "agent": "Coding",
            "event": "started",
        })

        await bus.publish("agent_started", {
            "agent": "coding",
            "task": task[:50],
        })

        logger.info(
            "[CodingAgent] Generating code..."
        )

        # Read research context
        research_context = context.get(
            "research", ""
        )

        prompt = f"""
Write Python code based on this task.

Task: {task}

Research result:
{research_context}

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

        code = self._clean_code(code)

        logger.info("[CodingAgent] Executing...")

        execution = await asyncio.to_thread(
            runtime.execute, code
        )

        log_tokens(250)

        logger.info(
            f"[CodingAgent] Output: "
            f"{execution['stdout'].strip()}"
        )

        result = AgentResult(
            success=execution.get("success", False),
            content=code,
            metadata={"execution": execution},
        )

        # Save to context for next agent
        context.set("coding", result.content)

        state.agent_status["coding"] = "completed"
        state.timeline.append({
            "agent": "Coding",
            "event": "completed",
        })

        await bus.publish("agent_completed", {
            "agent": "coding",
            "result": result.to_dict(),
        })

        return result

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
