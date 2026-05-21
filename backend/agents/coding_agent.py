from backend.utils.logger import logger, log_tokens
from backend.runtime.runtime_state import state
from backend.tools.python_runtime import PythonRuntime
from backend.llm.provider_factory import get_provider

runtime = PythonRuntime()
llm = get_provider()


class CodingAgent:

    def run(self, research_result):

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

        # LLM generates code
        prompt = f"""
Write Python code based on this research.

Research: {task_desc}

Requirements:
- Write complete, runnable code
- Include a print() statement for output
- Use only standard library

Return ONLY the Python code.
No markdown, no explanation.
"""

        code = llm.invoke(prompt)

        # Clean markdown code blocks
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

        logger.info(
            "[CodingAgent] Executing code..."
        )

        # Execute code
        execution_result = runtime.execute(code)

        # Auto-fix if failed
        if not execution_result["success"]:
            logger.info(
                "[CodingAgent] Code failed, "
                "attempting auto-fix..."
            )

            fixed_code = llm.invoke(
                f"""
Fix this Python code.

Code:
{code}

Error:
{execution_result["stderr"]}

Return ONLY the fixed Python code.
No markdown, no explanation.
"""
            )

            # Clean markdown code blocks
            if "```" in fixed_code:
                lines = fixed_code.split("\n")
                code_lines = []
                in_block = False
                for line in lines:
                    if line.strip().startswith("```"):
                        in_block = not in_block
                        continue
                    if in_block:
                        code_lines.append(line)
                fixed_code = "\n".join(code_lines)

            code = fixed_code
            execution_result = (
                runtime.execute(code)
            )

            logger.info(
                f"[CodingAgent] Auto-fix result: "
                f"{'success' if execution_result['success'] else 'failed'}"
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

        return {
            "code": code,
            "execution": execution_result
        }
