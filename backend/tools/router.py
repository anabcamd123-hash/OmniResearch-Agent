from backend.tools.registry import registry
from backend.llm.provider_factory import get_provider
from backend.utils.logger import logger
from backend.runtime.metrics import metrics


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

        context_text = ""
        if context:
            context_text = (
                "Context from past experiences:\n"
                + context
            )

        prompt = (
            f"You are a tool selection system.\n\n"
            f"Task:\n{task}\n\n"
            f"{context_text}\n\n"
            f"Available tools:\n{tools_text}\n\n"
            f"Return ONLY the tool name "
            f"(github/pdf/web/rag)."
        )

        tool_name = self.llm.invoke(prompt)

        tool_name = tool_name.strip().lower()

        if tool_name not in self.registry.tools:
            tool_name = "web"

        return tool_name

    async def execute(
        self,
        task: str,
        tool_name: str = None,
    ):

        if not tool_name:
            rag_tool = self.registry.get("rag")
            past_context = ""
            try:
                rag_result = await rag_tool.run(task)
                past_context = str(
                    rag_result.content
                )
            except Exception:
                pass

            tool_name = await self.select_tool(
                task, past_context
            )

        tool = self.registry.get(tool_name)

        if not tool:
            tool = self.registry.get("rag")

        metrics.tool_calls += 1
        metrics.tool_usage[tool_name] += 1

        logger.info(
            f"[ToolRouter] Selected: {tool_name}"
        )

        return await tool.run(task)


tool_router = ToolRouter()
