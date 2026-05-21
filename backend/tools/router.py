from backend.tools.registry import registry
from backend.llm.provider_factory import get_provider
from backend.utils.logger import logger


class ToolRouter:

    def __init__(self):

        self.registry = registry

        self.llm = get_provider()

    async def select_tool(
        self,
        task: str,
        context: str = "",
    ):

        tool_desc = self.registry.list_tools()

        tools_text = "\n".join([
            f"- {name}: {desc}"
            for name, desc in tool_desc.items()
        ])

        prompt = f"""
You are a tool selection system.

Task:
{task}

{f"Context from past experiences:\n{context}" if context else ""}

Available tools:
{tools_text}

Return ONLY the tool name (github/pdf/web/rag).
"""

        tool_name = self.llm.invoke(prompt)

        tool_name = tool_name.strip().lower()

        # Fallback validation
        if tool_name not in self.registry.tools:
            tool_name = "web"

        return tool_name

    async def execute(
        self,
        task: str,
        tool_name: str = None,
    ):

        if not tool_name:
            # Query past failures first
            rag_tool = self.registry.get("rag")
            past_context = ""
            try:
                rag_result = await rag_tool.run(task)
                past_context = str(
                    rag_result.get("context", "")
                )
            except Exception:
                pass

            tool_name = await self.select_tool(
                task, past_context
            )

        tool = self.registry.get(tool_name)

        if not tool:
            tool = self.registry.get("rag")

        logger.info(
            f"[ToolRouter] Selected: {tool_name}"
        )

        return await tool.run(task)


tool_router = ToolRouter()
