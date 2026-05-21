import httpx
from backend.utils.logger import logger


class MCPClient:

    async def call_tool(
        self,
        server_url: str,
        tool_name: str,
        arguments: dict,
    ):

        async with httpx.AsyncClient() as client:

            try:
                response = await client.post(
                    f"{server_url}/tools/call",
                    json={
                        "name": tool_name,
                        "arguments": arguments,
                    },
                    timeout=300,
                )

                response.raise_for_status()

                return response.json()

            except Exception as e:
                logger.info(
                    f"[MCP] Error calling "
                    f"{tool_name}: {e}"
                )
                return {"error": str(e)}


mcp_client = MCPClient()
