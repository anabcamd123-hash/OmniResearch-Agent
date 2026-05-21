from backend.tools.base import BaseTool


class RAGTool(BaseTool):

    name = "rag"
    description = (
        "Search historical knowledge "
        "and past experiences"
    )

    def __init__(self, rag_service):
        self.rag = rag_service

    async def run(self, input: str):

        results = await self.rag.query(
            input, top_k=5
        )

        return {
            "context": results,
            "sources": len(results),
        }
