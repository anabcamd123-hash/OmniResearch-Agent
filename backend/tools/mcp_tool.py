from backend.tools.base import BaseTool
from backend.tools.result import ToolResult


class MCPToolWrapper(BaseTool):

    def __init__(
        self,
        name: str,
        description: str,
        server_url: str,
        mcp_client,
    ):

        self.name = name
        self.description = description
        self.server_url = server_url
        self.mcp_client = mcp_client

    async def run(self, input: str):

        result = await self.mcp_client.call_tool(
            self.server_url,
            self.name,
            {"input": input},
        )

        if "error" in result:
            return ToolResult(
                success=False,
                content=result["error"],
            )

        return ToolResult(
            success=True,
            content=result,
        )
