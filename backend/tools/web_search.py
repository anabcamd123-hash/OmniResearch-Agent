from duckduckgo_search import DDGS
from backend.tools.base import BaseTool
from backend.tools.result import ToolResult


class WebSearchTool(BaseTool):

    name = "web"
    description = "Search the web using DuckDuckGo"

    async def run(self, input: str):

        with DDGS() as ddgs:
            results = list(
                ddgs.text(input, max_results=5)
            )

        return ToolResult(
            success=True,
            content=[
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                }
                for r in results
            ],
            metadata={"count": len(results)},
        )
