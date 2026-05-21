from backend.tools.base import BaseTool
from backend.tools.result import ToolResult


class RAGTool(BaseTool):

    name = "rag"
    description = "Search historical knowledge"

    def __init__(self, rag_service):
        self.rag = rag_service

    async def run(self, input: str):

        results = await self.rag.query(
            input, top_k=5
        )

        return ToolResult(
            success=True,
            content=results,
            metadata={"sources": len(results)},
        )
